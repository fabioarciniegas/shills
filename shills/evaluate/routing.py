# chat/routing.py
from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(r'^ws/film_scrapping/$', consumers.EchoConsumer),    
#    url(r'^ws/(?P<room_name>[^/]+)/$', consumers.ChatConsumer),
]
