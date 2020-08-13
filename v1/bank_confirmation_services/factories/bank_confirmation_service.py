from factory import SubFactory

from v1.banks.factories.bank import BankFactory
from v1.third_party.thenewboston.factories.confirmation_service import ConfirmationServiceFactory
from ..models.bank_confirmation_service import BankConfirmationService


class BankConfirmationServiceFactory(ConfirmationServiceFactory):
    bank = SubFactory(BankFactory)

    class Meta:
        model = BankConfirmationService
