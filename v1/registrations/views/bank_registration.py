from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

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
    def post(request):
        """
        description: Register a bank
        parameters:
          - name: signature
            required: true
            type: string
          - name: txs
            required: true
            type: array
            items:
              type: object
              properties:
                amount:
                  required: true
                  type: integer
                balance_key:
                  required: true
                  type: string
                recipient:
                  required: true
                  type: string
          - name: verifying_key_hex
            required: true
            type: string
        """

        serializer = BankRegistrationSerializerCreate(data=request.data, context={'request': request})
        if serializer.is_valid():
            bank_registration = serializer.save()
            return Response(
                BankRegistrationSerializer(bank_registration).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
