import pytest

from ..factories.bank_confirmation_service import BankConfirmationServiceFactory


@pytest.fixture
def bank_confirmation_services():
    yield BankConfirmationServiceFactory.create_batch(100)
