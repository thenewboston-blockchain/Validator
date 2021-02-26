from rest_framework.decorators import api_view
from rest_framework.response import Response

from thenewboston_validator.cache_tools.valid_confirmation_blocks import get_all_valid_confirmation_blocks


@api_view(['GET'])
def valid_confirmation_blocks_view(_):
    """Return list of valid confirmation blocks"""
    return Response({
        'valid_confirmation_blocks': get_all_valid_confirmation_blocks()
    })
