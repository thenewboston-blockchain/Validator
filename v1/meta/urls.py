from django.urls import path

from .views.block_chain import block_chain_view
from .views.block_queue import block_queue_view
from .views.confirmation_block_queue import confirmation_block_queue_view
from .views.head_block_hash import head_block_hash_view

urlpatterns = [

    # Block chain
    path('meta/block_chain', block_chain_view),

    # Block queue
    path('meta/block_queue', block_queue_view),

    # Confirmation block queue
    path('meta/confirmation_block_queue', confirmation_block_queue_view),

    # HEAD block hash
    path('meta/head_block_hash', head_block_hash_view),

]
