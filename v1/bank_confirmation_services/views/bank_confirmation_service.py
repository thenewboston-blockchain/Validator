from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from ..models.bank_confirmation_service import BankConfirmationService
from ..serializers.bank_confirmation_service import BankConfirmationServiceSerializer


class BankConfirmationServiceViewSet(
    ListModelMixin,
    GenericViewSet,
):
    """
    Bank confirmation services

    ---
    list:
      description: List bank confirmation services
    """

    queryset = BankConfirmationService.objects.all()
    serializer_class = BankConfirmationServiceSerializer
