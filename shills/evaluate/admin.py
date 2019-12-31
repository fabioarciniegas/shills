from django.contrib import admin

# Register your models here.
from .models import Film, Review

admin.site.register(Film)
admin.site.register(Review)
