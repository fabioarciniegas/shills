from django.db import models
import json
import operator
from math import log, exp
from scipy import stats
import metapy
from dynamic_preferences.registries import global_preferences_registry

global_preferences = global_preferences_registry.manager()

from django.core.validators import MinValueValidator, MaxValueValidator

class Film(models.Model):
    title = models.CharField(max_length=200,unique=True)
    scraped_completion = models.IntegerField(default=0)
    topics_completion = models.IntegerField(default=0)
    #json of the topic distributions for each review as processed by metapy
    topic_distributions = models.TextField()
    polarities_binned = models.TextField(default="")
    
    @property
    def topic_zscores(self):
        '''We don't want to save the zscores in db as they change 
        constantly with topic distributions changes and are easy to 
        calculate on the fly. However, we don't want to return empty
        zscores either when individual reviews are requested, so we put 
        the attribute behind this prop which ensures topic distribution
        is calculated first.
        '''
        self.calculate_topic_z_scores()
        return self.__topic_zscores

    @topic_zscores.setter
    def topic_zscores(self,value):
        self.__topic_zscores = value

    @property
    def rating_zscores(self):
        self.rating_distribution()
        return self.__rating_zscores

    @rating_zscores.setter
    def rating_zscores(self,value):
        self.__rating_zscores = value


    def rating_distribution(self):
        total_count = 0.00001
        nz = 0.0000000001
        rating_count = {0:nz,1:nz,2:nz,3:nz,4:nz,5:nz,6:nz,7:nz,8:nz,9:nz,10:nz}
        for r in self.review_set.all():
            if r.rating not in rating_count:
                rating_count[r.rating] = 1
            else:
                rating_count[r.rating] += 1
            total_count +=1
        scores = stats.zscore([v for k,v in rating_count.items()])
        # zip makes into tuples, dict makes first in tuple key
        # remember rating z-scores given this distribution (don't save them, they
        # change with distribution changes and are cheap to calculate)
        self.rating_zscores = dict(zip([k for k,v in rating_count.items()],scores))
        # TODO: move json.dumps to a template tag and keep model cleaner
        return json.dumps([[k,(v/total_count)*100] for k,v in rating_count.items()])
            
#TODO: clean up, separating z_scores calculation from generation of favorite topic         distribution
    def calculate_topic_z_scores(self):
        pis = json.loads(self.topic_distributions)
        topics_mass = {}
        total_mass =0.0000001
        ri = self.review_set.all().iterator()
#                total_mass +=pi
        for doc in pis:
            sorted_x = sorted(doc.items(), key=operator.itemgetter(1))
            for topic,pi in sorted_x[0:1]:
                if topic not in topics_mass:
                    topics_mass[topic] = 1 #instead of pi
                else:
                    topics_mass[topic] += 1
            total_mass += 1
        scores = stats.zscore([v for k,v in topics_mass.items()])
        self.topic_zscores = dict(zip([k for k,v in topics_mass.items()],scores))
        return json.dumps([[k,(v/total_mass)*100] for k,v in topics_mass.items()])
    
    def __str__(self):
        return self.title


class Review(models.Model):
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    rating = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(10.0)])
    text = models.TextField(blank=False)
    congruency_score = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],default=0)
    convolution_score = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],default=0)
    topicality_score = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],default=0)
    topics_distribution = models.TextField(default="{}")
    sentiment_polarity = models.FloatField(validators=[MinValueValidator(-100.0), MaxValueValidator(100.0)],default=0)
    sentiment_polarity_bin = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],default=0)
    cached_score = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],default=0)
    manually_flagged_as_shady = models.BooleanField(default=False)
    
    @property
    def pis(self):
        return json.loads(self.topics_distribution)
    
    def top_topic(self,top=0):
        if len(self.pis.items()) == 0:
            return ""
        topics_sorted = sorted(self.pis.items(), key=operator.itemgetter(1))
        if(len(topics_sorted[top])>0):
            return topics_sorted[top][0]
        return ""

    def percentage_z_to_threshold(self,z,t):
        clipped_percentage = min(100.0,100.0*(abs(z)/(t+0.001)))
#        print("z: %f  - threshold z: %f , percent == %f"%(z,t,clipped_percentage))
        return clipped_percentage
        
    def update_topicality_score(self):
        tz = self.film.topic_zscores[self.top_topic()]
        tt = global_preferences['scores__topic_outlier_threshold']
        rz = self.film.rating_zscores[self.rating]
        rt = global_preferences['scores__rating_outlier_threshold']
        t = self.percentage_z_to_threshold(tz,tt)
        r = self.percentage_z_to_threshold(rz,rt)
        self.topicality_score = 2*(t * r) / (t + r)
#        print("topic z: %f  - rating z: %f , harmonic == %f"%(t,r,self.topicality_score))
        self.save()

    def update_congruency_score(self):
        x = abs(self.rating - self.sentiment_polarity_bin)/2.0
        # 0.8 by default. Make smaller if we don't trust our predictions that much :)
        k = global_preferences['scores__bin_decay_rate']
        self.congruency_score = 100.0*(1.0-exp(k*x))
        self.save()

    def update_language_score(self):
        # updated as part of evaluate topics. Does not change until forced in preferences.
        return
        
        
    def score(self):
        '''Combine all three scores into a final [0-100] score via harmonic mean'''
        self.update_topicality_score()
        self.update_congruency_score()
        self.update_language_score()
        cs = self.congruency_score
        ts = self.topicality_score
        vs = self.convolution_score
        csw = global_preferences['scores__non_predictive_language_weight']
        tsw = global_preferences['scores__outlier_topics_and_ratings_weight']
        vsw = global_preferences['scores__backhanded_language_weight']
        self.cached_score = (cs*csw+ts*tsw+vs*vsw)/100.0
        self.save()
        return self.cached_score


    def __str__(self):
        return "Rating: " + str(self.rating) + " Score: " + str(self.cached_score) + " (" + str(self.congruency_score) + "," + str(self.convolution_score) + "," +  str(self.topicality_score) + ") '" + self.text[0:60] + "'"

class Topic(models.Model):
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    
