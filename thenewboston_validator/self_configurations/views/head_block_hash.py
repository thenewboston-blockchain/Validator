from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response

from thenewboston_validator.cache_tools.cache_keys import HEAD_BLOCK_HASH


@api_view(['GET'])
def head_block_hash_view(_):
    """Return the HEAD_BLOCK_HASH"""
    return Response(cache.get(HEAD_BLOCK_HASH))
