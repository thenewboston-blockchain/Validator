from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.viewsets import ViewSet

from thenewboston_validator.decorators.nodes import is_signed_message
from ..serializers.primary_validator_updated import PrimaryValidatorUpdatedSerializer


class PrimaryValidatorUpdatedViewSet(ViewSet):
    """
    Primary validator updated

    ---
    create:
      description: Primary validator updated notice from bank
    """

    serializer_class = PrimaryValidatorUpdatedSerializer

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

        return Response({}, status=HTTP_200_OK)
