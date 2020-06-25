from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from v1.decorators.nodes import is_signed_by_primary_validator
from ..serializers.confirmation_block import ConfirmationBlockSerializerCreate


# confirmation_blocks
class ConfirmationBlockView(APIView):

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
