from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from thenewboston.constants.errors import ERROR
from thenewboston.constants.network import HEAD_HASH_LENGTH

from v1.cache_tools.valid_confirmation_blocks import get_valid_confirmation_block


# valid_confirmation_blocks/{block_identifier}
class ValidConfirmationBlockDetail(APIView):

    @staticmethod
    def get(request, block_identifier):
        """
        description: View individual valid confirmation block
        """

        if len(block_identifier) != HEAD_HASH_LENGTH:
            return Response(
                {ERROR: f'block_identifier must be {HEAD_HASH_LENGTH} characters long'},
                status=status.HTTP_403_FORBIDDEN
            )

        valid_confirmation_block = get_valid_confirmation_block(block_identifier=block_identifier)

        if not valid_confirmation_block:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(valid_confirmation_block)
