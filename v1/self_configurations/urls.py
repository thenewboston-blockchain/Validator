from django.urls import path

from .views.head_block_hash import head_block_hash_view
from .views.self_configuration import SelfConfigurationDetail

urlpatterns = [

    # Self configuration
    path('config', SelfConfigurationDetail.as_view()),

    # Head block hash
    path('head_block_hash', head_block_hash_view),

]
