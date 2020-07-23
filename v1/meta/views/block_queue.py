from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response

from v1.cache_tools.cache_keys import BLOCK_QUEUE


@api_view(['GET'])
def block_queue_view(_):
    """
    Return BLOCK_QUEUE
    """

    return Response({
        'block_queue': cache.get(BLOCK_QUEUE)
    })
