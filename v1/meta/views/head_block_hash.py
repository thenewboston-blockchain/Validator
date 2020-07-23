from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response

from v1.cache_tools.cache_keys import HEAD_BLOCK_HASH


@api_view(['GET'])
def head_block_hash_view(_):
    """
    Return HEAD_BLOCK_HASH
    """

    return Response({
        'head_block_hash': cache.get(HEAD_BLOCK_HASH)
    })
