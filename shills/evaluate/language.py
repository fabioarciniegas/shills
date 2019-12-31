import re
import time
import urllib
import requests
import operator
from .models import Review
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
from .metapy_templates import stopwords, toml, linetoml, all_toml
from scipy import stats

global_preferences = global_preferences_registry.manager()

async def export_and_retrain(loop=None):
    write_all_reviews_for_metapy()
    #TODO: save the trained model to disk somehow (can be done in C++ but apparently not exported in metapy)

def write_all_reviews_for_metapy():
    fn = "manually_tagged_backhanded"
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
    
    written=0
    with open(fn+".toml","w") as fout:
        fout.write(all_toml)

    makedirs(fn)            
        
    with open(path.join(fn,"line.toml"),"w") as fout:
        fout.write(linetoml)

    with open(fn+"-stopwords.txt","w") as fout:
        fout.write(stopwords)

    corpus = path.join(fn,fn+".dat")
    with open(corpus,"w") as fout:
        for r in Review.objects.all():
            fout.write(r.text+"\n")
            written +=1

    written_labels = 0
    corpus_labels = path.join(fn,fn+".dat.labels")
    with open(corpus_labels,"w") as fout:
        for r in Review.objects.all():
            c = "backhanded" if r.manually_flagged_as_shady else "ok"
            fout.write(c+"\n")
            written_labels +=1

#    assert(written == written_labels)



                
    
def language_classify_in_thread(loop,film,force):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(export_and_retrain(loop))
    global_preferences['scores__retrain_before_next_evaluation'] = False

