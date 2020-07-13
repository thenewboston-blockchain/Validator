from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from v1.cache_tools.cache_keys import BLOCK_QUEUE
from v1.decorators.nodes import is_signed_bank_block
from v1.tasks.block_queue import process_block_queue


# bank_blocks
class BankBlockView(APIView):

    @staticmethod
    @is_signed_bank_block
    def post(request):
        """
        description: Add a bank block to the queue
        """

        # TODO: Serializer will check block formatting
        # TODO: These initial checks should not hit the SQL database
        # TODO: Also throw an error if this validator is not a primary validator
        # TODO: If everything is good, add the block to the block queue

        block = request.data.get('block')
        queue = cache.get(BLOCK_QUEUE)

        if queue:
            queue.append(block)
        else:
            queue = [block]

        cache.set(BLOCK_QUEUE, queue, None)
        process_block_queue.delay()

        return Response({}, status=status.HTTP_200_OK)
