from django.urls import path
from rest_framework.routers import SimpleRouter

from .views.head_block_hash import head_block_hash_view
from .views.self_configuration import SelfConfigurationViewSet

router = SimpleRouter(trailing_slash=False)
router.register('config', SelfConfigurationViewSet, basename='config')

urlpatterns = [

    # Head block hash
    path('head_block_hash', head_block_hash_view),

]
