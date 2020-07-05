from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from v1.decorators.nodes import is_signed_message
from ..serializers.connection_request import ConnectionRequestSerializerCreate


# connection_requests
class ConnectionRequestView(APIView):

    @staticmethod
    @is_signed_message
    def post(request):
        """
        description: Create connection request
        """

        serializer = ConnectionRequestSerializerCreate(
            data=request.data['message'],
            context={'request': request}
        )
        if serializer.is_valid():
            results = serializer.save()
            return Response(results, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
