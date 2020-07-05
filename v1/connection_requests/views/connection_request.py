from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models.connection_request import ConnectionRequest
from ..serializers.connection_request import ConnectionRequestSerializer, ConnectionRequestSerializerCreate


# connection_requests
class ConnectionRequestView(APIView):

    @staticmethod
    def get(request):
        """
        description: List connection requests
        """

        connection_requests = ConnectionRequest.objects.all()
        return Response(ConnectionRequestSerializer(connection_requests, many=True).data)

    @staticmethod
    def post(request):
        """
        description: Create connection request
        """

        serializer = ConnectionRequestSerializerCreate(data=request.data, context={'request': request})
        if serializer.is_valid():
            connection_request = serializer.save()
            return Response(ConnectionRequestSerializer(connection_request).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
