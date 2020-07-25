from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from v1.decorators.nodes import is_signed_message
from v1.self_configurations.serializers.self_configuration import SelfConfigurationSerializer
from ..serializers.upgrade_request import UpgradeRequestSerializer


# upgrade_request
class UpgradeRequestView(APIView):

    @staticmethod
    @is_signed_message
    def post(request):
        """
        description: Bank asking a confirmation validator to upgrade to a primary validator
        """

        serializer = UpgradeRequestSerializer(
            data={
                **request.data['message'],
                'node_identifier': request.data['node_identifier']
            },
            context={'request': request}
        )
        if serializer.is_valid():
            self_configuration = serializer.save()
            return Response(
                SelfConfigurationSerializer(self_configuration).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
