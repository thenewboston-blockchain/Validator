from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from v1.decorators.nodes import is_signed_message
from v1.status_updates.management.check_bank import is_most_trusted_bank
from v1.status_updates.management.promote_validator import promote_confirmation_validator


class StatusUpdateView(APIView):
    @is_signed_message
    def post(self, request):
        node_data = request.data
        bank_node_identifier = node_data.get('node_identifier')
        is_trusted = is_most_trusted_bank(node_identifier=bank_node_identifier)

        if is_trusted:
            promote_confirmation_validator()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
