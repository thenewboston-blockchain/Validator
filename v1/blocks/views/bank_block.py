from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from thenewboston.blocks.signatures import verify_signature
from thenewboston.utils.tools import sort_and_encode


# bank_blocks
class BankBlockView(APIView):

    @staticmethod
    def post(request):
        """
        description: Add a bank block to the queue
        """

        block = request.data.get('block')
        message = sort_and_encode(block)
        verify_signature(
            account_number=request.data.get('confirmation_identifier'),
            signature=request.data.get('signature'),
            message=message
        )
        return Response(status=status.HTTP_200_OK)
