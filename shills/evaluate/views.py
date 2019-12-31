from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseRedirect
from django.template import loader
from .models import Film, Review
from .forms import SearchForm
from .scraper  import scrape_in_thread
from .topics import evaluate_in_thread
from .language import language_classify_in_thread
from .bins import weight_predicted_bin_to_rating
from django.shortcuts import render
from django.utils.safestring import mark_safe
import json
import asyncio
import random
import threading
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.forms import global_preference_form_builder
from django.contrib import messages

global_preferences = global_preferences_registry.manager()

def all_reviews(request,film_id=1):
    template = loader.get_template('evaluate/all_reviews.html')
    try:    
        f = Film.objects.get(id=film_id)
    except Film.DoesNotExist:
        return HttpResponseRedirect("/")
    context = {'f': f,
               'reviews' : f.review_set.order_by('-cached_score')

    }
    return HttpResponse(template.render(context, request))


# Create your views here.
def index(request,film_id=1):
    template = loader.get_template('evaluate/index.html')
    st = global_preferences['scores__total_threshold']
    try:    
        f = Film.objects.get(id=film_id)
    except Film.DoesNotExist:
        f = Film(title="<try one on the left>")
    if request.method == 'GET':
        force = request.GET.get('force') or 0
        if force:
            f.scraped_completion = 100
            f.topics_completion = 10
        random_review = random.randint(3,60)
        context = {
            'version': '0.4',
            'topic_form' : global_preference_form_builder(preferences=['topics__k','scores__topic_outlier_threshold','scores__rating_outlier_threshold']),

            'sentiment_form' : global_preference_form_builder(preferences=['scores__bin_decay_rate']),
            'language_form' : global_preference_form_builder(preferences=['scores__retrain_before_next_evaluation']),            
            
            'score_form' : global_preference_form_builder(preferences=['scores__total_threshold','scores__non_predictive_language_weight','scores__outlier_topics_and_ratings_weight','scores__backhanded_language_weight']),'form' : SearchForm(),
            'films' : Film.objects.order_by('-id')[0:15],
            'film' : f,
            'show_recalculate' : (not global_preferences['scores__retrain_before_next_evaluation']), # TODO: and total number of concurrent scrapes and calculates below n
            'num_shills' : f.review_set.filter(cached_score__gte=st).count(),
            'num_suspicious' : (f.review_set.filter(congruency_score__gte=st) |
                                f.review_set.filter(convolution_score__gte=st) |
                                f.review_set.filter(topicality_score__gte=st)).count(),
            'shill_reviews' : f.review_set.order_by('-cached_score')[0:3],
            'fair_reviews' : f.review_set.order_by('cached_score')[0:4],
            'mixed_reviews' : f.review_set.order_by('cached_score')[random_review:random_review+3],
            'topics_json' : f.topic_distributions,
            'predicted_to_rating_weights' : json.dumps(weight_predicted_bin_to_rating(f)),
            'total_reviews' : len(f.review_set.all()),
            'done_scrapping' : f.scraped_completion == 100,
            'done_topics' : f.topics_completion == 100,            
        }
        if f.scraped_completion == 100 and f.topics_completion < 100:
            f.save()
            loop = asyncio.new_event_loop()
            t = threading.Thread(target=evaluate_in_thread,args=(loop,f,force))
            t.start()
#    messages.warning(request, 'must fixed bad names')
    return HttpResponse(template.render(context, request))


def films(request):
    f = Film.objects
    context = {'films': f}
    return render(request, 'evaluate/films.html', context)


def search(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            f = None
            title = form.cleaned_data['title']
            try:
                f = Film.objects.get(title=title)
            except Film.DoesNotExist:
                f = None
            if not f:
                f = Film(title=title)
                f.save()
            loop = asyncio.new_event_loop()
            if f.scraped_completion < 100:
                t = threading.Thread(target=scrape_in_thread,args=(loop,title))
                t.start()
        return HttpResponseRedirect("/%d"%f.id)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SearchForm()
    return render(request, 'evaluate/search.html', {'form': form})

def preferences(request):
    if request.method == 'POST':
        form = global_preference_form_builder(preferences=[
            ('k','topics'),('total_threshold','scores'),
            ('topic_outlier_threshold','scores'),('rating_outlier_threshold','scores'),
            ('bin_decay_rate','scores'),('retrain_before_next_evaluation','scores'),
            ('non_predictive_language_weight','scores'),('outlier_topics_and_ratings_weight','scores'),('backhanded_language_weight','scores')
        ])(request.POST)
        if form.is_valid():
            for k,v in form.cleaned_data.items():
#                print("%s = %s" % (k,v))
                if v is not None:
                    global_preferences[k] = v

    messages.info(request, 'Changes in preferences affect scores. Click "Recalculate Scores" on a given movie to update its analysis')                    
    if global_preferences['scores__retrain_before_next_evaluation'] == True:
        loop = asyncio.new_event_loop()
        t = threading.Thread(target=language_classify_in_thread,args=(loop,1,0))
        t.start()
        messages.warning(request, 'Language classification is now being retrained based on manual tagging you have done to review data. "Recalculate Scores" button will be hidden until process finishes to avoid inconsistencies.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# TODO: hacky. turn this into restful and csrf-aware post end point.
def toggle_shady_review(request,review_id=1):
    try:    
        r = Review.objects.get(id=review_id)
        r.manually_flagged_as_shady = not r.manually_flagged_as_shady
        r.save()
    except Review.DoesNotExist:
        return JsonResponse({"message":"review not found"})
    r.manually_flagged_as_shady = True
    return JsonResponse({"message":"ok"})
    
