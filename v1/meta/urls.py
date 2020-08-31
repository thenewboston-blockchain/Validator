from django.urls import path

from .views.block_chain import block_chain_view
from .views.block_queue import block_queue_view
from .views.head_block_hash import head_block_hash_view
from .views.queued_confirmation_blocks import queued_confirmation_blocks_view
from .views.valid_confirmation_blocks import valid_confirmation_blocks_view

urlpatterns = [

    # Block chain
    path('meta/block_chain', block_chain_view),

    # Block queue
    path('meta/block_queue', block_queue_view),

    # HEAD block hash
    path('meta/head_block_hash', head_block_hash_view),

    # Queued confirmation blocks
    path('meta/queued_confirmation_blocks', queued_confirmation_blocks_view),

    # Valid confirmation blocks
    path('meta/valid_confirmation_blocks', valid_confirmation_blocks_view),

]
