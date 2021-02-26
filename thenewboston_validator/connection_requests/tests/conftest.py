import pytest
from thenewboston.accounts.manage import create_account
from thenewboston.serializers.primary_validator import PrimaryValidatorSerializer
from thenewboston.utils.format import format_address
from thenewboston.utils.signed_requests import generate_signed_request

from thenewboston_validator.banks.serializers.bank import BankSerializer
from thenewboston_validator.validators.serializers.validator import ValidatorSerializer


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
def bank_config_no_primary_validator_info(bank):
    bank_config = BankSerializer(bank).data
    bank_config['node_type'] = 'BANK'
    yield bank_config


@pytest.fixture
def validator_config(validator, primary_validator_config):
    validator_config = ValidatorSerializer(validator).data
    validator_config['node_type'] = 'CONFIRMATION_VALIDATOR'
    validator_config['primary_validator'] = primary_validator_config
    yield validator_config


@pytest.fixture
def validator_config_primary_node(validator, primary_validator_config):
    validator_config = ValidatorSerializer(validator).data
    validator_config['node_type'] = 'PRIMARY_VALIDATOR'
    validator_config['primary_validator'] = primary_validator_config
    yield validator_config


@pytest.fixture
def config_unknown_node(validator, primary_validator_config):
    validator_config = ValidatorSerializer(validator).data
    validator_config['node_type'] = 'UNKNOWN_NODE'
    validator_config['primary_validator'] = primary_validator_config
    yield validator_config


@pytest.fixture
def bank_connection_requests_signed_request(bank, signing_key):
    yield generate_signed_request(
        data={
            'ip_address': bank.ip_address,
            'port': bank.port,
            'protocol': bank.protocol,
        },
        nid_signing_key=signing_key
    )


@pytest.fixture
def validator_connection_requests_signed_request(validator, signing_key):
    yield generate_signed_request(
        data={
            'ip_address': validator.ip_address,
            'port': validator.port,
            'protocol': validator.protocol,
        },
        nid_signing_key=signing_key
    )


@pytest.fixture
def bank_connection_requests_signed_request_new_node_identifier(bank):
    signing_key, _ = create_account()
    yield generate_signed_request(
        data={
            'ip_address': bank.ip_address,
            'port': bank.port,
            'protocol': bank.protocol,
        },
        nid_signing_key=signing_key
    )


@pytest.fixture
def validator_connection_requests_signed_request_new_node_identifier(validator):
    signing_key, _ = create_account()
    yield generate_signed_request(
        data={
            'ip_address': validator.ip_address,
            'port': validator.port,
            'protocol': validator.protocol,
        },
        nid_signing_key=signing_key
    )


@pytest.fixture
def validator_connection_requests_signed_request_connect_to_itself(primary_validator_configuration):
    signing_key, _ = create_account()
    yield generate_signed_request(
        data={
            'ip_address': primary_validator_configuration.ip_address,
            'port': primary_validator_configuration.port,
            'protocol': primary_validator_configuration.protocol,
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


@pytest.fixture
def validator_address(validator):
    yield format_address(
        ip_address=validator.ip_address,
        port=validator.port,
        protocol=validator.protocol
    )
