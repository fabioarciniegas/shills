import re
import time
import urllib
import requests
import operator
import sys
import metapy
import json
from textblob import TextBlob
import asyncio
import websockets
from math import ceil
from os import makedirs, path,remove
import shutil
from dynamic_preferences.registries import global_preferences_registry
from .metapy_templates import stopwords, toml, linetoml
from scipy import stats

global_preferences = global_preferences_registry.manager()

async def extract_topics(loop=None,film=None,force=False):
    write_topics_for_metapy(film,force)
    if(film.topics_completion == 100 and not force):
        return
    fn = "film_"+str(film.id)
    num_topics = global_preferences['topics__k']
    async with websockets.connect(
        'ws://localhost:8000/ws/film_scrapping/') as websocket:    
#            metapy.log_to_stderr()
            await websocket.send(json.dumps({'film': film.id, 'percentage':'10'}))
            fidx = metapy.index.make_forward_index(fn+'.toml')
            dset = metapy.learn.Dataset(fidx)
            lda_inf = metapy.topics.LDACollapsedVB(dset, num_topics=num_topics, alpha=1.0, beta=0.01)
            lda_inf.run(num_iters=1000)
            lda_inf.save(fn+'_lda-cvb0')
            model = metapy.topics.TopicModel(fn+'_lda-cvb0')
            tns = name_topics(model,fidx)
            distributions = []
            relative_id = 0
            # WARNING: this could potentially be buggy if for whatever reason
            # the number of items written for metapy is less than
            # the number of children. 
            count = film.review_set.all().count()
            for relative_id in range(0,count):
                d = {}
                for ij in range(0,num_topics):
                    d[tns[ij]] = model.topic_distribution(relative_id).probability(ij)
                distributions.append(d)
            film.topic_distributions = json.dumps(distributions)
            film.save()
            await websocket.send(json.dumps({'film': film.id, 'percentage':'15'}))

            ## ---- Calculate film polarity beans
            ri = film.review_set.all().iterator()
            polarities = []
            saved_reviews=0
            for doc in distributions:
                sorted_x = sorted(doc.items(), key=operator.itemgetter(1))
                r = next(ri)
                r.topics_distribution = json.dumps({i[0]:i[1] for i in sorted_x})
                b=TextBlob(r.text)
                r.sentiment_polarity = b.sentiment[0]
                r.save()
                polarities.append(r.sentiment_polarity)
                saved_reviews+=1
                p = str(ceil(saved_reviews/count*100))
                await websocket.send(json.dumps({'film': film.id, 'percentage':p}))
            film.topics_completion=100
            observations = [1] * saved_reviews
            film.polarities_binned = json.dumps(stats.binned_statistic(polarities,polarities,'mean',bins=11)[0].tolist())
            film.save()

            ## ----- Train classifier
            ## (should be read from disk instead of doing it for every film but
            ## metapy does not seem to export save for classifiers)
            if path.exists("manually_tagged_backhanded"):
                fidx_tc = metapy.index.make_forward_index('manually_tagged_backhanded.toml')
                dset_tc = metapy.classify.MulticlassDataset(fidx_tc)
                view_tc = metapy.classify.MulticlassDatasetView(dset_tc)
                view_tc.shuffle()
                training_tc = view_tc[0:len(view_tc)]
                nb_tc = metapy.classify.NaiveBayes(training_tc)
                review_fidx = metapy.index.make_forward_index("film_%d.toml"%film.id)
                dset_film = metapy.classify.MulticlassDataset(review_fidx)
                view_film = metapy.classify.MulticlassDatasetView(dset_film)
                testing_film = view_film[0:len(view_film)]
            ## ----- Calculate scores given current configuration
            saved_reviews=0
            for r in film.review_set.all():
                #TODO: re-encapsulate as part of score() when metapy can save a classifier
                if (nb_tc.classify(testing_film[saved_reviews].weights) == "backhanded"):
                    r.convolution_score = 100.0
                else:
                    r.convolution_score = 0.0
                r.score()
                r.save()
                saved_reviews+=1
                p = str(ceil(saved_reviews/count*100))
                await websocket.send(json.dumps({'film': film.id, 'percentage':p}))
            
            await websocket.send(json.dumps({'film': film.id, 'percentage':'100'}))


def write_topics_for_metapy(film,force=False):
    fn = "film_"+str(film.id)
    if(force):
        if path.exists(fn+".toml"):
            remove(fn+".toml")
        if path.exists(fn+"-stopwords.txt"):
            remove(fn+"-stopwords.txt")
        if path.exists(fn):
            shutil.rmtree(fn)
        if path.exists(fn+"-idx"):
            shutil.rmtree(fn+"-idx")
        if path.exists(fn+"_lda-cvb0.phi.bin"):            
            remove(fn+"_lda-cvb0.phi.bin")
        if path.exists(fn+"_lda-cvb0.theta.bin"):            
            remove(fn+"_lda-cvb0.theta.bin")
    
    if path.isfile(fn+".toml"):
        print("already saved as files")
        return
    written=0
    with open(fn+".toml","w") as fout:
        fout.write(toml % (film.id,film.id,film.id))

    with open(fn+"-stopwords.txt","w") as fout:
        fout.write(stopwords)
        # Ignore the title of the film for topics
        for w in film.title.split():
            fout.write(w+"\n")

    makedirs(fn)            
    corpus = path.join(fn,fn+".dat")
    with open(corpus,"w") as fout:
        for r in film.review_set.all():
            fout.write(r.text+"\n")
            written +=1
                
    with open(path.join(fn,"line.toml"),"w") as fout:
        fout.write(linetoml)



def name_topics(model,index):
    names = []
    num_topics = global_preferences['topics__k']    
    for i in range(0,num_topics):
        for term in model.top_k(tid=i,k=num_topics):
            representative = index.term_text(term[0])
            if representative not in names:
                names.append(representative)
                break

    second = []
    for i in range(0,num_topics):
        for term in model.top_k(tid=i,k=num_topics):
            representative = index.term_text(term[0])
            if representative not in second and representative != names[i]:
                second.append(representative)
                break
            
    for i in range(0,num_topics):
        names[i] += "," + second[i] + ""
            
    return names
                
        
    
def evaluate_in_thread(loop,film,force):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(extract_topics(loop,film,force))

