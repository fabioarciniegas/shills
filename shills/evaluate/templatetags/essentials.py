from django import template
from math import floor,ceil
from dynamic_preferences.registries import global_preferences_registry

global_preferences = global_preferences_registry.manager()

register = template.Library()

@register.filter(name='times') 
def times(number):
    return range(number)


@register.filter(name='full_stars') 
def full_stars(number):
    return range(int(floor(number/2)))

@register.filter(name='half_stars') 
def half_stars(number):
    return range(int(ceil((number/2) % 1)))


@register.filter(name='shill') 
def shill(score):
    img = "<img src='http://placehold.it/%d/%s/fff?text=%s' class='img-circle' />"
    text = "OK"
    color = "008811"
    size = 30
    if score > global_preferences['scores__total_threshold']:
        size = 30
        text = "S"
        color = "d9534f"
    return img % (size,color,text)
