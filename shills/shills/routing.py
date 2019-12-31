# mysite/routing.py
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
import evaluate.routing
import evaluate

application = ProtocolTypeRouter({

#    'scraper': ChannelNameRouter({
#        "scrape-movie": evaluate.consumers.ScraperConsumer,
#        }),
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            evaluate.routing.websocket_urlpatterns
        )
    ),
})
