import pytest
from thenewboston.third_party.factory.utils import build_json

from ..factories.bank import BankFactory


@pytest.fixture
def bank_fake_data():
    data = build_json(BankFactory)
    data['confirmation_expiration'] = str(data['confirmation_expiration'])
    yield data


@pytest.fixture
def banks():
    yield BankFactory.create_batch(100)
