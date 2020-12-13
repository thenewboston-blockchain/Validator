import pytest
from v1.banks.serializers.bank import BankSerializer
from thenewboston.serializers.primary_validator import PrimaryValidatorSerializer
from thenewboston.utils.signed_requests import generate_signed_request
from thenewboston.utils.format import format_address
from thenewboston.accounts.manage import create_account


@pytest.fixture
def primary_validator_config(primary_validator_configuration):
    yield PrimaryValidatorSerializer(primary_validator_configuration).data


@pytest.fixture
def bank_config(bank, primary_validator_config):
    bank_config = BankSerializer(bank).data
    bank_config['node_type'] = 'BANK'
    bank_config['primary_validator'] = primary_validator_config
    yield bank_config


@pytest.fixture
def bank_connection_requests_signed_request(bank, signing_key):
    yield generate_signed_request(
        data={
            "ip_address": bank.ip_address,
            "port": bank.port,
            "protocol": bank.protocol,
        },
        nid_signing_key=signing_key
    )

@pytest.fixture
def bank_connection_requests_signed_request_new_node_identifier(bank):
    signing_key, _ = create_account()
    yield generate_signed_request(
        data={
            "ip_address": bank.ip_address,
            "port": bank.port,
            "protocol": bank.protocol,
        },
        nid_signing_key=signing_key
    )


@pytest.fixture
def bank_address(bank):
    yield format_address(
        ip_address=bank.ip_address,
        port=bank.port,
        protocol=bank.protocol
    )