import pytest
from nacl.encoding import HexEncoder
from nacl.signing import SigningKey
from thenewboston.utils.messages import get_message_hash
from thenewboston.utils.signed_requests import generate_signed_request

from v1.meta.helpers.block_identifier import get_initial_block_identifier


@pytest.fixture
def initial_block_identifier(primary_validator_configuration):
    return get_initial_block_identifier()


@pytest.fixture
def confirmation_block_data(block_data, initial_block_identifier, primary_validator_signing_key, account_number):
    yield generate_signed_request(
        data={
            'block': block_data,
            'block_identifier': initial_block_identifier,
            'updated_balances': [
                {
                    'account_number': block_data['account_number'],
                    'balance': 1,
                    'balance_lock': get_message_hash(message=block_data['message']),
                }
            ],
        },
        nid_signing_key=primary_validator_signing_key,
    )


@pytest.fixture
def primary_validator_signing_key():
    yield SigningKey(
        '6f812a35643b55a77f71c3b722504fbc5918e83ec72965f7fd33865ed0be8f81',
        encoder=HexEncoder,
    )


@pytest.fixture
def signed_confirmation_block_history_request(validator, signing_key, initial_block_identifier):
    yield generate_signed_request(
        data={
            'block_identifier': initial_block_identifier
        },
        nid_signing_key=signing_key,
    )
