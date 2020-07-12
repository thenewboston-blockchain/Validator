from django.conf import settings
from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from thenewboston.constants.errors import ERROR
from thenewboston.constants.network import HEAD_HASH_LENGTH
from thenewboston.utils.messages import get_message_hash

from v1.cache_tools.cache_keys import get_confirmation_block_cache_key


# confirmation_block_chain_segment/{block_identifier}
class ConfirmationBlockChainSegmentView(APIView):

    @staticmethod
    def get(request, block_identifier):
        """
        description: List confirmation block chain segment (starting at the block_identifier)
        """

        if len(block_identifier) != HEAD_HASH_LENGTH:
            return Response(
                {ERROR: f'block_identifier must be {HEAD_HASH_LENGTH} characters long'},
                status=status.HTTP_403_FORBIDDEN
            )

        confirmation_block_cache_key = get_confirmation_block_cache_key(block_identifier=block_identifier)
        confirmation_block = cache.get(confirmation_block_cache_key)

        if not confirmation_block:
            return Response(status=status.HTTP_404_NOT_FOUND)

        counter = 0
        results = []

        while confirmation_block and counter < settings.CONFIRMATION_BLOCK_CHAIN_SEGMENT_LENGTH:
            results.append(confirmation_block)
            message = confirmation_block['message']
            message_hash = get_message_hash(message=message)
            confirmation_block_cache_key = get_confirmation_block_cache_key(block_identifier=message_hash)
            confirmation_block = cache.get(confirmation_block_cache_key)
            counter += 1

        return Response(results)
