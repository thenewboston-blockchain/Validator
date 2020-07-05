from rest_framework.response import Response
from rest_framework.views import APIView

from ..models.connection_request import ConnectionRequest
from ..serializers.connection_request import ConnectionRequestSerializer


# connection_requests
class ConnectionRequestView(APIView):

    @staticmethod
    def get(request):
        """
        description: List connection requests
        """

        connection_requests = ConnectionRequest.objects.all()
        return Response(ConnectionRequestSerializer(connection_requests, many=True).data)
