from channels.routing import ProtocolTypeRouter, URLRouter

from v1.lean import routing as clean_routing
from v1.crawl import routing as crawl_routing

application = ProtocolTypeRouter({
    'websocket': URLRouter(
        clean_routing.websocket_urlpatterns +
        crawl_routing.websocket_urlpatterns
    )
})
