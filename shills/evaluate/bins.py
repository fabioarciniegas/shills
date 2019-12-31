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
import pandas

global_preferences = global_preferences_registry.manager()

num_topics = global_preferences['topics__k']

def rate(bins,polarity):
#    print(polarity)
    if polarity > bins[-1]:
        return len(bins)-1
    i = 0

#   As discussed in the literature [1], people don't really use the
#   full range of the ratings scale but instead slant to the right.
#   this roughly compensates for that effect.
#   [1] http://www.cs.cornell.edu/home/llee/papers/pang-lee-stars.home.html
    slant = 3
    while (i < len(bins)) and bins[i] < polarity:
        i += 1
    return min(10,0.0 + i+slant)

def weight_predicted_bin_to_rating(film):
    '''
    Map the flow of predicted ratings to actual ratings.
    Produce a series of arrays [x , y , w] where x is the predicted bin (e.g. 3 stars),
    y is the actual rating (e.g 2 stars) and w is the weight, that is the
    number of reviews that match conditions x and y.
    '''
    if film.polarities_binned == "":
        return
    
    bins = json.loads(film.polarities_binned)
    s_p = ['predicted '+str((0.0 +i)/2) for i in range(0,11)]
    s_g = ['ground '+str((0.0 +i)/2) for i in range(0,11)]
    ones = [1 for i in range(0,11)]        
    df = pandas.DataFrame(list(zip(s_p,s_g,ones)),columns=['From','To','Weigth'])
    i = 11
    for r in film.review_set.all():
        r.sentiment_polarity_bin = rate(bins,r.sentiment_polarity)
        r.save()
        df.loc[i] = ['predicted '+str(r.sentiment_polarity_bin/2),'ground '+str(r.rating/2),1]        
        i += 1
    df = df.sort_values(by=['From','To'],ascending=False)

    return df.values.tolist()
