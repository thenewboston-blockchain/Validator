from rest_framework.response import Response
from rest_framework.views import APIView

from ..models.bank_confirmation_service import BankConfirmationService
from ..serializers.bank_confirmation_service import BankConfirmationServiceSerializer


# bank_confirmation_services
class BankConfirmationServiceView(APIView):

    @staticmethod
    def get(request):
        """
        description: List bank confirmation services
        """

        bank_confirmation_services = BankConfirmationService.objects.all()
        return Response(BankConfirmationServiceSerializer(bank_confirmation_services, many=True).data)
