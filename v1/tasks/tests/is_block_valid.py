import pytest
from thenewboston.constants.network import BANK, PRIMARY_VALIDATOR

from v1.self_configurations.helpers.self_configuration import get_self_configuration
from v1.tasks.block_queue import is_block_valid


@pytest.mark.django_db
def get_self_account_number():
    self_configuration = get_self_configuration(exception_class=RuntimeError)
    return self_configuration.account_number


@pytest.fixture(autouse=True)
def primary_validator(primary_validator_configuration):
    pass


def test_incorrect_amount():
    """
    Block with incorrect amount(s) is not valid

    - original (valid) amount of non-fee Tx is 425
    """
    data = [
        (0, False),
        (23, False),
        (424, False),
        (425, True),
        (426, False),
        (999, False),
    ]

    for amount, expected_result in data:
        block = {
            'account_number': '0cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb',
            'message': {
                'balance_key': '0cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb',
                'txs': [
                    {
                        'amount': amount,
                        'recipient': '484b3176c63d5f37d808404af1a12c4b9649cd6f6769f35bdf5a816133623fbc'
                    },
                    {
                        'amount': 1,
                        'fee': BANK,
                        'recipient': '5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8'
                    },
                    {
                        'amount': 4,
                        'fee': PRIMARY_VALIDATOR,
                        'recipient': get_self_account_number()
                    }
                ]
            },
            'signature': '2c2aae162c0de7d7c66856a1728e06c26fe1732a8073721ca0cf6d22f868be07158f7256ba02e34eb913aea0f3c16cc135bacc3631a74f97b1fb7a3463059707'
        }
        is_valid, account_balance = is_block_valid(block=block)
        assert is_valid == expected_result


def test_incorrect_balance_key():
    """Block with incorrect balance key is not valid"""
    data = [
        ('bacon', False),
        ('484b3176c63d5f37d808404af1a12c4b9649cd6f6769f35bdf5a816133623fbc', False),
        ('db1a9ac3c356ab744ab4ad5256bb86c2f6dfaa7c1aece1f026a08dbd8c7178f2', False),
        ('0cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb', True),
    ]

    for balance_key, expected_result in data:
        block = {
            'account_number': '0cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb',
            'message': {
                'balance_key': balance_key,
                'txs': [
                    {
                        'amount': 425,
                        'recipient': '484b3176c63d5f37d808404af1a12c4b9649cd6f6769f35bdf5a816133623fbc'
                    },
                    {
                        'amount': 1,
                        'fee': BANK,
                        'recipient': '5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8'
                    },
                    {
                        'amount': 4,
                        'fee': PRIMARY_VALIDATOR,
                        'recipient': get_self_account_number()
                    }
                ]
            },
            'signature': '2c2aae162c0de7d7c66856a1728e06c26fe1732a8073721ca0cf6d22f868be07158f7256ba02e34eb913aea0f3c16cc135bacc3631a74f97b1fb7a3463059707'
        }
        is_valid, account_balance = is_block_valid(block=block)
        assert is_valid == expected_result


def test_incorrect_signature():
    """Block with incorrect signature is not valid"""
    data = [
        (
            'bacon',
            False
        ),
        (
            '282248de23b11281927c402ffb402a8c26d3ae1e638a4d25aa91272763478248cc37df76925eb8bcd9b0260cbee4fbf56e0e7826617053796ace6117a472d304',
            False
        ),
        (
            'a5538dbdf6b0a7d43c99e735ebbb64791341011bea311c0783295a6b85c3dc907d791f5be77b562b45151e07ebcbf809ccfc8292ec841283ff2f00b2bffe7109',
            False
        ),
        (
            '2c2aae162c0de7d7c66856a1728e06c26fe1732a8073721ca0cf6d22f868be07158f7256ba02e34eb913aea0f3c16cc135bacc3631a74f97b1fb7a3463059707',
            True
        ),
    ]

    for signature, expected_result in data:
        block = {
            'account_number': '0cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb',
            'message': {
                'balance_key': '0cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb',
                'txs': [
                    {
                        'amount': 425,
                        'recipient': '484b3176c63d5f37d808404af1a12c4b9649cd6f6769f35bdf5a816133623fbc'
                    },
                    {
                        'amount': 1,
                        'fee': BANK,
                        'recipient': '5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8'
                    },
                    {
                        'amount': 4,
                        'fee': PRIMARY_VALIDATOR,
                        'recipient': get_self_account_number()
                    }
                ]
            },
            'signature': signature
        }
        is_valid, account_balance = is_block_valid(block=block)
        assert is_valid == expected_result


def test_invalid_amount():
    """
    Treasury balance = 10,000

    Total amount = 10,005
    """
    block = {
        'account_number': '0cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb',
        'message': {
            'balance_key': '0cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb',
            'txs': [
                {
                    'amount': 10000,
                    'recipient': '484b3176c63d5f37d808404af1a12c4b9649cd6f6769f35bdf5a816133623fbc'
                },
                {
                    'amount': 1,
                    'fee': BANK,
                    'recipient': '5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8'
                },
                {
                    'amount': 4,
                    'fee': PRIMARY_VALIDATOR,
                    'recipient': get_self_account_number()
                }
            ]
        },
        'signature': '85a255d720bf5897d65bad7ad410bab672d34bd0871ba20c1cb910a084d298e194fb86559eee093ab5d8c83dc7a785a235a3febb5d78f256066a8b70a271110a'
    }
    is_valid, account_balance = is_block_valid(block=block)
    assert not is_valid


def test_missing_transaction():
    """Block with missing transaction should be invalid"""
    block = {
        'account_number': '0cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb',
        'message': {
            'balance_key': '0cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb',
            'txs': [
                {
                    'amount': 1,
                    'recipient': '5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8'
                },
                {
                    'amount': 4,
                    'fee': BANK,
                    'recipient': 'ad1f8845c6a1abb6011a2a434a079a087c460657aad54329a84b406dce8bf314'
                }
            ]
        },
        'signature': 'cfcba759125dfbaaefa627c4a41db4e5052705875d01228e5e280e13d403483fff495157b53192a6c1032ee815429f4979c0b4beb10d259fae3692123cf01f0d'
    }
    is_valid, account_balance = is_block_valid(block=block)
    assert not is_valid


def test_valid_block():
    """Valid block is validated correctly"""
    block = {
        'account_number': '0cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb',
        'message': {
            'balance_key': '0cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb',
            'txs': [
                {
                    'amount': 425,
                    'recipient': '484b3176c63d5f37d808404af1a12c4b9649cd6f6769f35bdf5a816133623fbc'
                },
                {
                    'amount': 1,
                    'fee': BANK,
                    'recipient': '5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8'
                },
                {
                    'amount': 4,
                    'fee': PRIMARY_VALIDATOR,
                    'recipient': get_self_account_number()
                }
            ]
        },
        'signature': '2c2aae162c0de7d7c66856a1728e06c26fe1732a8073721ca0cf6d22f868be07158f7256ba02e34eb913aea0f3c16cc135bacc3631a74f97b1fb7a3463059707'
    }
    is_valid, account_balance = is_block_valid(block=block)
    assert is_valid
