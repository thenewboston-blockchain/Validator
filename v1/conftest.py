import os

import pytest
from django.conf import settings
from django.core.management import call_command
from pytest_django.migrations import DisableMigrations
from thenewboston.accounts.manage import create_account
from thenewboston.blocks.block import generate_block
from thenewboston.constants.network import PRIMARY_VALIDATOR
from thenewboston.third_party.pytest.client import UserWrapper
from thenewboston.verify_keys.verify_key import encode_verify_key

from v1.banks.factories.bank import BankFactory
from v1.cache_tools.helpers import rebuild_cache
from v1.self_configurations.helpers.self_configuration import get_self_configuration
from v1.self_configurations.management.commands.initialize_test_confirmation_validator import (
    FIXTURES_DIR as CONFIRMATION_VALIDATOR_FIXTURES_DIR
)
from v1.self_configurations.management.commands.initialize_test_primary_validator import (
    FIXTURES_DIR as PRIMARY_VALIDATOR_FIXTURES_DIR
)
from v1.validators.factories.validator import ValidatorFactory


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
def block_data(account_data, encoded_account_number, random_encoded_account_number):
    signing_key, account_number = create_account()

    yield generate_block(
        account_number=account_number,
        balance_lock=encode_verify_key(
            verify_key=account_number,
        ),
        signing_key=signing_key,
        transactions=[
            {
                'amount': 4,
                'fee': PRIMARY_VALIDATOR,
                'recipient': 'ad1f8845c6a1abb6011a2a434a079a087c460657aad54329a84b406dce8bf314'
            },
            {
                'amount': 1,
                'recipient': random_encoded_account_number
            }
        ]
    )


@pytest.fixture
def client():
    yield UserWrapper(None)


@pytest.fixture
def confirmation_validator_configuration(monkeypatch):
    load_validator_fixtures(CONFIRMATION_VALIDATOR_FIXTURES_DIR)
    monkeypatch.setenv('NETWORK_SIGNING_KEY', '7a3359729b41f953d52818e787a312c8576e179e2ee50a2e4f28c4596b12dce0')

    self_configuration = get_self_configuration(exception_class=RuntimeError)
    rebuild_cache(head_block_hash=self_configuration.root_account_file_hash)

    yield self_configuration


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(transactional_db):
    pass


@pytest.fixture
def encoded_account_number(account_number):
    yield encode_verify_key(verify_key=account_number)


def load_validator_fixtures(fixtures_dir):
    fixture_files = [
        'validator.json',
        'account.json',
        'bank.json',
        'self_configuration.json',
        'user.json'
    ]
    for fixture_file in fixture_files:
        fixture = os.path.join(fixtures_dir, fixture_file)
        call_command('loaddata', fixture, verbosity=1)


@pytest.fixture(scope='session', autouse=True)
def migrations_disabled():
    settings.MIGRATION_MODULES = DisableMigrations()
    yield None


@pytest.fixture
def primary_validator(encoded_account_number):
    yield ValidatorFactory(
        node_identifier=encoded_account_number,
    )


@pytest.fixture
def primary_validator_configuration(monkeypatch):
    load_validator_fixtures(PRIMARY_VALIDATOR_FIXTURES_DIR)
    monkeypatch.setenv('NETWORK_SIGNING_KEY', '6f812a35643b55a77f71c3b722504fbc5918e83ec72965f7fd33865ed0be8f81')
    yield get_self_configuration(exception_class=RuntimeError)


@pytest.fixture
def random_encoded_account_number():
    _, account_number = create_account()
    yield encode_verify_key(verify_key=account_number)


@pytest.fixture
def signing_key(account_data):
    key, account_number = account_data
    yield key


@pytest.fixture(autouse=True)
def use_fake_redis(settings):
    """Using fake Redis for running tests in parallel."""
    settings.DJANGO_REDIS_CONNECTION_FACTORY = 'thenewboston.third_party.django_redis.pool.FakeConnectionFactory'
    settings.CACHES['default']['OPTIONS']['REDIS_CLIENT_CLASS'] = 'fakeredis.FakeStrictRedis'


@pytest.fixture
def validator(encoded_account_number):
    yield ValidatorFactory(node_identifier=encoded_account_number)
