import pytest
from nacl.encoding import HexEncoder
from nacl.signing import SigningKey
from thenewboston.accounts.manage import create_account
from thenewboston.blocks.block import generate_block
from thenewboston.blocks.signatures import generate_signature
from thenewboston.utils.tools import sort_and_encode
from thenewboston.verify_keys.verify_key import encode_verify_key, get_verify_key


@pytest.fixture
def bank_signing_key():
    yield SigningKey(
        'e5e5fec0dcbbd8b0a76c67204823678d3f243de7a0a1042bb3ecf66285cd9fd4',
        encoder=HexEncoder
    )


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
                'amount': 1,
                'recipient': random_encoded_account_number
            }
        ]
    )


@pytest.fixture
def random_encoded_account_number():
    _, account_number = create_account()
    yield encode_verify_key(verify_key=account_number)


@pytest.fixture
def signed_block(block_data, bank_signing_key):
    yield {
        'block': block_data,
        'node_identifier': encode_verify_key(
            verify_key=get_verify_key(
                signing_key=bank_signing_key,
            ),
        ),
        'signature': generate_signature(
            message=sort_and_encode(block_data),
            signing_key=bank_signing_key,
        ),
    }
