from factory import SubFactory
from thenewboston.factories.confirmation_service import ConfirmationServiceFactory

from v1.banks.factories.bank import BankFactory
from ..models.bank_confirmation_service import BankConfirmationService


class BankConfirmationServiceFactory(ConfirmationServiceFactory):
    bank = SubFactory(BankFactory)

    class Meta:
        model = BankConfirmationService
