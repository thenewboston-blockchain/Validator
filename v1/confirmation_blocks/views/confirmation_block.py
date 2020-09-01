from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

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
            serializer.save()
            process_confirmation_block_queue.delay()
            return Response({}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
