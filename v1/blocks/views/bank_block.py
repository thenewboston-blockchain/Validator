from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from v1.constants.cache_keys import BANK_BLOCK_QUEUE
from v1.tasks.blocks import process_bank_block_queue


# bank_blocks
class BankBlockView(APIView):

    @staticmethod
    def post(request):
        """
        description: Add a bank block to the queue
        """

        # TODO: Serializer will check everything except point balances (registered bank, block formatting, etc...)
        # TODO: Also throw an error if this validator is not a primary validator
        # TODO: If everything is good, add it to the bank block queue

        queue = cache.get(BANK_BLOCK_QUEUE)

        if queue:
            queue.append(request.data)
        else:
            queue = [request.data]

        cache.set(BANK_BLOCK_QUEUE, queue, None)
        process_bank_block_queue.delay()

        return Response({}, status=status.HTTP_200_OK)
