from channels.routing import ProtocolTypeRouter, URLRouter

from thenewboston_validator.clean import routing as clean_routing
from thenewboston_validator.crawl import routing as crawl_routing

application = ProtocolTypeRouter({
    'websocket': URLRouter(
        clean_routing.websocket_urlpatterns + crawl_routing.websocket_urlpatterns
    )
})
