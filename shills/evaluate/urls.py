from django.urls import path
from django.conf.urls import url


from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('films/', views.films, name='films'),
    path('search/', views.search, name='search'),
    path('preferences/', views.preferences, name='preferences'),    
    path('<int:film_id>/', views.index, name='detail'),
    path('<int:film_id>/all', views.all_reviews, name='all_reviews'),
    path('tgs/<int:review_id>/', views.toggle_shady_review, name='toggle_shade'),    
#    url(r'^(?P<room_name>[^/]+)/$', views.room, name='room'),

]
