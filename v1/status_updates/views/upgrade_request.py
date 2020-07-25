from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from v1.decorators.nodes import is_signed_message
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
            serializer.save()
            return Response({}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
