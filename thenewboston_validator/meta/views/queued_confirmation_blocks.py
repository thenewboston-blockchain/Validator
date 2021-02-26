from rest_framework.decorators import api_view
from rest_framework.response import Response

from thenewboston_validator.cache_tools.queued_confirmation_blocks import get_all_queued_confirmation_blocks


@api_view(['GET'])
def queued_confirmation_blocks_view(_):
    """Return list of queued confirmation blocks"""
    return Response({
        'queued_confirmation_blocks': get_all_queued_confirmation_blocks()
    })
