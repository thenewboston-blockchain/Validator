from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response

from v1.cache_tools.cache_keys import CONFIRMATION_BLOCK_QUEUE


@api_view(['GET'])
def confirmation_block_queue_view(_):
    """
    Return CONFIRMATION_BLOCK_QUEUE
    """

    return Response({
        'confirmation_block_queue': cache.get(CONFIRMATION_BLOCK_QUEUE)
    })
