from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.viewsets import ViewSet

from v1.decorators.nodes import is_signed_message
from ..serializers.confirmation_block_history import ConfirmationBlockHistorySerializer


class ConfirmationBlockHistoryViewSet(ViewSet):
    """
    Confirmation block history

    ---
    create:
      description: Confirmation block history request from a confirmation validator
    """

    serializer_class = ConfirmationBlockHistorySerializer

    @is_signed_message
    def create(self, request):
        serializer = self.serializer_class(
            data={
                **request.data['message'],
                'node_identifier': request.data['node_identifier']
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(request.data, status=HTTP_200_OK)
