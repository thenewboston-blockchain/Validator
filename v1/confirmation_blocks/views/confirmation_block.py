from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from thenewboston.constants.errors import ERROR
from thenewboston.constants.network import HEAD_HASH_LENGTH

from v1.cache_tools.cache_keys import HEAD_BLOCK_HASH, get_confirmation_block_cache_key
from v1.decorators.nodes import is_signed_by_primary_validator
from v1.tasks.confirmation_block_queue import process_confirmation_block_queue
from ..serializers.confirmation_block import ConfirmationBlockSerializerCreate


# confirmation_blocks
class ConfirmationBlockView(APIView):

    @staticmethod
    @is_signed_by_primary_validator
    def post(request):
        """
        description: Add a confirmation block to the queue
        """

        serializer = ConfirmationBlockSerializerCreate(data=request.data['message'])
        if serializer.is_valid():
            block_identifier = serializer.save()
            head_block_hash = cache.get(HEAD_BLOCK_HASH)

            if block_identifier == head_block_hash:
                process_confirmation_block_queue.delay()

            return Response({}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# confirmation_blocks/{block_identifier}
class ConfirmationBlockDetail(APIView):

    @staticmethod
    def get(request, block_identifier):
        """
        description: View individual confirmation block
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

        return Response(confirmation_block)
