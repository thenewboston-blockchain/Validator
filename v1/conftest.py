import pytest
from django.core.management import call_command
from thenewboston.accounts.manage import create_account
from thenewboston.third_party.pytest.client import UserWrapper
from thenewboston.verify_keys.verify_key import encode_verify_key

from v1.self_configurations.helpers.self_configuration import get_self_configuration
from v1.validators.factories.validator import ValidatorFactory


@pytest.fixture
def account_data():
    yield create_account()


@pytest.fixture
def account_number(account_data):
    signing_key, account_number = account_data
    yield account_number


@pytest.fixture
def client():
    yield UserWrapper(None)


@pytest.fixture
def confirmation_validator_configuration(monkeypatch):
    call_command(
        'initialize_test_confirmation_validator',
        ip='127.0.0.1'
    )
    monkeypatch.setenv('NETWORK_SIGNING_KEY', '7a3359729b41f953d52818e787a312c8576e179e2ee50a2e4f28c4596b12dce0')
    yield get_self_configuration(exception_class=RuntimeError)


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def encoded_account_number(account_number):
    yield encode_verify_key(verify_key=account_number)


@pytest.fixture
def primary_validator_configuration(monkeypatch):
    call_command(
        'initialize_test_primary_validator',
        ip='127.0.0.1'
    )
    monkeypatch.setenv('NETWORK_SIGNING_KEY', '6f812a35643b55a77f71c3b722504fbc5918e83ec72965f7fd33865ed0be8f81')
    yield get_self_configuration(exception_class=RuntimeError)


@pytest.fixture
def validator(encoded_account_number):
    yield ValidatorFactory(node_identifier=encoded_account_number)
