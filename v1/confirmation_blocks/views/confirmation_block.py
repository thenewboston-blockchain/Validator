from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from v1.cache_tools.cache_keys import get_confirmation_block_cache_key
from v1.decorators.nodes import is_signed_by_primary_validator
from v1.self_configurations.helpers.self_configuration import get_self_configuration
from v1.tasks.blocks import get_message_hash
from ..serializers.confirmation_block import ConfirmationBlockSerializerCreate


# confirmation_blocks
class ConfirmationBlockView(APIView):

    @staticmethod
    def get(request):
        """
        description: List confirmation block
        """

        self_configuration = get_self_configuration(exception_class=RuntimeError)
        confirmation_block_cache_key = get_confirmation_block_cache_key(block_identifier=self_configuration.root_account_file_hash)
        confirmation_block = cache.get(confirmation_block_cache_key)

        if not confirmation_block:
            return Response(status=status.HTTP_200_OK)

        results = []

        while confirmation_block:
            results.append(confirmation_block)
            message = confirmation_block['message']
            message_hash = get_message_hash(message=message)
            confirmation_block_cache_key = get_confirmation_block_cache_key(block_identifier=message_hash)
            confirmation_block = cache.get(confirmation_block_cache_key)

        return Response(results)

    @staticmethod
    @is_signed_by_primary_validator
    def post(request):
        """
        description: Add a confirmation block to the queue
        """

        serializer = ConfirmationBlockSerializerCreate(
            data=request.data['message'],
            context={'request': request}
        )
        if serializer.is_valid():
            confirmation_block_message = serializer.save()
            return Response(confirmation_block_message, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
