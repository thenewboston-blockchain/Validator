from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from thenewboston.constants.network import PRIMARY_VALIDATOR

from thenewboston_validator.cache_tools.cache_keys import BLOCK_QUEUE, BLOCK_QUEUE_CACHE_LOCK_KEY
from thenewboston_validator.decorators.nodes import is_signed_bank_block
from thenewboston_validator.self_configurations.helpers.self_configuration import get_self_configuration
from thenewboston_validator.tasks.block_queue import process_block_queue
from ..serializers.block import BlockSerializer

"""
Banks will request a new primary validator if an error status (status code >= 400) is returned
This view should check the block formatting only and not the validity of the transaction
"""


class BankBlockViewSet(ViewSet):
    """
    Bank block

    ---
    create:
      description: Add a block to the queue
    """

    @staticmethod
    def add_block_to_queue(block):
        with cache.lock(BLOCK_QUEUE_CACHE_LOCK_KEY):
            queue = cache.get(BLOCK_QUEUE)

            if queue:
                queue.append(block)
            else:
                queue = [block]

            cache.set(BLOCK_QUEUE, queue, None)
        process_block_queue.delay()

    @staticmethod
    @is_signed_bank_block
    def create(request):
        self_configuration = get_self_configuration(exception_class=RuntimeError)

        if self_configuration.node_type != PRIMARY_VALIDATOR:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

        block = request.data.get('block')

        serializer = BlockSerializer(
            data=block,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        BankBlockViewSet.add_block_to_queue(block)

        return Response(block, status=status.HTTP_200_OK)
