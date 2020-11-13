from faker import Faker
from nacl.encoding import HexEncoder
from nacl.signing import SigningKey
import pytest
from thenewboston.constants.network import BLOCK_IDENTIFIER_LENGTH
from thenewboston.utils.messages import get_message_hash
from thenewboston.utils.signed_requests import generate_signed_request


@pytest.fixture
def block_identifier():
    yield Faker().pystr(max_chars=BLOCK_IDENTIFIER_LENGTH)


@pytest.fixture
def confirmation_block_data(block_data, block_identifier, primary_validator_signing_key, account_number):
    yield generate_signed_request(
        data={
            'block': block_data,
            'block_identifier': block_identifier,
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
