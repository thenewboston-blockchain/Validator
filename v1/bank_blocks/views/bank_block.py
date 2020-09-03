from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from thenewboston.constants.network import PRIMARY_VALIDATOR
from thenewboston.serializers.network_block import NetworkBlockSerializer

from v1.cache_tools.cache_keys import BLOCK_QUEUE
from v1.decorators.nodes import is_signed_bank_block
from v1.self_configurations.helpers.self_configuration import get_self_configuration
from v1.tasks.block_queue import process_block_queue

"""
Banks will request a new primary validator if an error status (status code >= 400) is returned
This view should check the block formatting only and not the validity of the transaction
"""


# bank_blocks
class BankBlockView(APIView):

    @staticmethod
    def add_block_to_queue(block):
        """
        Add block to the queue
        """

        # TODO: Improved caching system

        queue = cache.get(BLOCK_QUEUE)

        if queue:
            queue.append(block)
        else:
            queue = [block]

        cache.set(BLOCK_QUEUE, queue, None)
        process_block_queue.delay()

    @staticmethod
    @is_signed_bank_block
    def post(request):
        """
        description: Add a block to the queue
        """

        self_configuration = get_self_configuration(exception_class=RuntimeError)

        if self_configuration.node_type != PRIMARY_VALIDATOR:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

        block = request.data.get('block')

        serializer = NetworkBlockSerializer(
            data=block,
            context={'request': request}
        )

        if serializer.is_valid():
            BankBlockView.add_block_to_queue(block)
            return Response({}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
