from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response
from thenewboston.utils.messages import get_message_hash

from v1.cache_tools.cache_keys import get_confirmation_block_cache_key
from ..helpers.block_identifier import get_initial_block_identifier


@api_view(['GET'])
def block_chain_view(_):
    """
    Return block chain
    """

    block_chain = {}
    block_identifier = get_initial_block_identifier()
    confirmation_block_cache_key = get_confirmation_block_cache_key(block_identifier=block_identifier)
    confirmation_block = cache.get(confirmation_block_cache_key)

    i = 0

    while confirmation_block:
        block_chain[i] = confirmation_block
        block = confirmation_block['message']['block']
        block_identifier = get_message_hash(message=block['message'])
        confirmation_block_cache_key = get_confirmation_block_cache_key(block_identifier=block_identifier)
        confirmation_block = cache.get(confirmation_block_cache_key)

    return Response({
        'block_chain': block_chain
    })
