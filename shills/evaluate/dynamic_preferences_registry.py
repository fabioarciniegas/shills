from dynamic_preferences.types import BooleanPreference, StringPreference, FloatPreference, IntegerPreference, BooleanPreference
from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.users.registries import user_preferences_registry
from django.forms import ValidationError

# we create some section objects to link related preferences together

scraper = Section('scraper')
topics = Section('topics')
scores = Section('scores')

# We start with a global preference
@global_preferences_registry.register
class ScraperDelay(IntegerPreference):
    section = scraper
    name = 'delay'
    default = 1
    required = False

@global_preferences_registry.register
class TopicsK(IntegerPreference):
    section = topics
    name = 'k'
    default = 8
    required = False


@global_preferences_registry.register
class ScoresThreshold(FloatPreference):
    section = scores
    name = 'total_threshold'
    default = 10.0
    required = False
    def validate(self, value):
        if value < 0.0 or value > 100.0:
            raise ValidationError('[0,100] values only')


@global_preferences_registry.register
class ConvolutionWeight(FloatPreference):
    section = scores
    name = 'backhanded_language_weight'
    default = 10.0
    required = False
    def validate(self, value):
        if value < 0.0 or value > 100.0:
            raise ValidationError('[0,100] values only')
        
@global_preferences_registry.register
class TopicalityWeight(FloatPreference):
    section = scores
    name = 'outlier_topics_and_ratings_weight'
    default = 45.0
    required = False
    def validate(self, value):
        if value < 0.0 or value > 100.0:
            raise ValidationError('[0,100] values only')

@global_preferences_registry.register
class CongruencyWeight(FloatPreference):
    section = scores
    name = 'non_predictive_language_weight'
    default = 45.0
    required = False
    def validate(self, value):
        if value < 0.0 or value > 100.0:
            raise ValidationError('[0,100] values only')





    
@global_preferences_registry.register
class TopicOutlierThreshold(FloatPreference):
    '''
    how big does a z-score have to be before we consider the
    topic an outlier?
    '''
    section = scores
    name = 'topic_outlier_threshold'
    default = 2.0
    required = False

@global_preferences_registry.register
class RatingOutlierThreshold(FloatPreference):
    section = scores
    name = 'rating_outlier_threshold'
    default = 2.0
    required = False

@global_preferences_registry.register
class BinDifferenceDecayRate(FloatPreference):
    section = scores
    name = 'bin_decay_rate'
    default = -1.0
    required = False
    def validate(self, value):
        if value > 0.0:
            raise ValidationError('negative values only')

@global_preferences_registry.register
class RetrainLanguage(BooleanPreference):
    section = scores
    name = 'retrain_before_next_evaluation'
    default = False
    required = False
        
    
@global_preferences_registry.register
class MaintenanceMode(BooleanPreference):
    name = 'maintenance_mode'
    default = False
