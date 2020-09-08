from channels.routing import ProtocolTypeRouter, URLRouter

from v1.crawl import routing as crawl_routing

application = ProtocolTypeRouter({
    'websocket': URLRouter(
        crawl_routing.websocket_urlpatterns
    )
})
