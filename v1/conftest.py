import pytest
from django.core.management import call_command

from v1.self_configurations.helpers.self_configuration import get_self_configuration
from v1.third_party.pytest.client import UserWrapper


@pytest.fixture
def client():
    yield UserWrapper(None)


@pytest.fixture
def confirmation_validator_configuration():
    call_command(
        'initialize_test_primary_validator',
        ip='127.0.0.1'
    )
    yield get_self_configuration(exception_class=RuntimeError)


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass
