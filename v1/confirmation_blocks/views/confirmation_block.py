from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from v1.cache_tools.cache_keys import CONFIRMATION_BLOCK_QUEUE
from v1.decorators.nodes import is_signed_by_primary_validator
from v1.self_configurations.helpers.self_configuration import get_self_configuration
from v1.tasks.blocks import process_confirmation_block_queue


# confirmation_blocks
class ConfirmationBlockView(APIView):

    @staticmethod
    @is_signed_by_primary_validator
    def post(request):
        """
        description: Add a confirmation block to the queue
        """

        # TODO: Serializer will check everything except point balances (block formatting, etc...)
        # TODO: If everything is good, add the entire confirmation block to the confirmation block queue

        self_configuration = get_self_configuration(exception_class=RuntimeError)
        print(self_configuration)

        message = request.data.get('message')
        print(message)

        queue = cache.get(CONFIRMATION_BLOCK_QUEUE)

        if queue:
            queue.append(request.data)
        else:
            queue = [request.data]

        cache.set(CONFIRMATION_BLOCK_QUEUE, queue, None)
        process_confirmation_block_queue.delay()

        return Response({}, status=status.HTTP_200_OK)
