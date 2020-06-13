from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from v1.cache_tools.cache_keys import CONFIRMATION_BLOCK_QUEUE
from v1.tasks.blocks import process_confirmation_block_queue


# confirmation_blocks
class ConfirmationBlockView(APIView):

    @staticmethod
    def post(request):
        """
        description: Add a confirmation block to the queue
        """

        # TODO: Serializer will check everything except point balances (from PV, block formatting, etc...)
        # TODO: Throw an error if this IS the primary validator (should not be accepting confirmed blocks, creates them)
        # TODO: If everything is good, add the entire confirmation block to the confirmation block queue

        queue = cache.get(CONFIRMATION_BLOCK_QUEUE)

        if queue:
            queue.append(request.data)
        else:
            queue = [request.data]

        cache.set(CONFIRMATION_BLOCK_QUEUE, queue, None)
        process_confirmation_block_queue.delay()

        return Response({}, status=status.HTTP_200_OK)
