import pytest
from thenewboston.accounts.manage import create_account
from thenewboston.verify_keys.verify_key import encode_verify_key

from v1.third_party.factory.utils import build_json
from ..factories.bank import BankFactory


@pytest.fixture
def account_data():
    yield create_account()


@pytest.fixture
def account_number(account_data):
    signing_key, account_number = account_data
    yield account_number


@pytest.fixture
def bank(encoded_account_number):
    yield BankFactory(node_identifier=encoded_account_number)


@pytest.fixture
def bank_fake_data():
    data = build_json(BankFactory)
    data['confirmation_expiration'] = str(data['confirmation_expiration'])
    yield data


@pytest.fixture
def banks():
    yield BankFactory.create_batch(100)


@pytest.fixture
def encoded_account_number(account_number):
    yield encode_verify_key(verify_key=account_number)
