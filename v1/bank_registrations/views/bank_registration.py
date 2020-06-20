from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from v1.decorators.nodes import is_signed_request
from ..models.bank_registration import BankRegistration
from ..serializers.bank_registration import BankRegistrationSerializer, BankRegistrationSerializerCreate


# bank_registrations
class BankRegistrationView(APIView):

    @staticmethod
    def get(request):
        """
        description: List bank registrations
        """

        bank_registrations = BankRegistration.objects.all()
        return Response(BankRegistrationSerializer(bank_registrations, many=True).data)

    @staticmethod
    @is_signed_request
    def post(request):
        """
        description: Register a bank
        """

        serializer = BankRegistrationSerializerCreate(
            data={
                **request.data['message'],
                'network_identifier': request.data['network_identifier']
            },
            context={'request': request}
        )
        if serializer.is_valid():
            bank_registration = serializer.save()
            return Response(
                BankRegistrationSerializer(bank_registration).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
