from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.viewsets import ViewSet

from thenewboston_validator.decorators.nodes import is_signed_message
from thenewboston_validator.self_configurations.serializers.self_configuration import SelfConfigurationSerializer
from ..serializers.upgrade_request import UpgradeRequestSerializer


class UpgradeRequestViewSet(ViewSet):
    """
    Upgrade request

    ---
    create:
      description: Bank asking a confirmation validator to upgrade to a primary validator
    """

    serializer_class = UpgradeRequestSerializer

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
        self_configuration = serializer.save()

        return Response(
            SelfConfigurationSerializer(self_configuration).data,
            status=HTTP_200_OK
        )
