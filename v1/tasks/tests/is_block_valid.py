import pytest

from v1.tasks.block_queue import is_block_valid


@pytest.fixture(autouse=True)
def primary_validator(primary_validator_configuration):
    pass


def test_incorrect_amount():
    """
    Block with incorrect amount(s) is not valid
    - amount of 426 was changed from 425
    """
    data = [
        (23, False),
        (0, False),
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
                        'recipient': '5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8'
                    },
                    {
                        'amount': 4,
                        'recipient': 'ad1f8845c6a1abb6011a2a434a079a087c460657aad54329a84b406dce8bf314'
                    }
                ]
            },
            'signature': '72457709aca384c0a8659112d26773b5c32468fad4dd1329c88445979f2896d05ce52bc1d3990cd6dbec65f0fdb378b7685515f865e304f97b2a3ef9ab19a20d'
        }

        is_valid, account_balance = is_block_valid(block=block)
        assert is_valid == expected_result


def test_incorrect_balance_key():
    """
    Block with incorrect balance key is not valid
    """

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
                        'amount': 4,
                        'recipient': '484b3176c63d5f37d808404af1a12c4b9649cd6f6769f35bdf5a816133623fbc'
                    },
                    {
                        'amount': 1,
                        'recipient': '5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8'
                    },
                    {
                        'amount': 4,
                        'recipient': 'ad1f8845c6a1abb6011a2a434a079a087c460657aad54329a84b406dce8bf314'
                    }
                ]
            },
            'signature': '9c95931ff252b24d53ea899c0766f313675d05e0a522c81ef860415e7ebae88098f6f120ffb7dbe8f6acb3969aaab39be9bbb3eb6445f5f8d99b84a162107a0a'
        }
        is_valid, account_balance = is_block_valid(block=block)
        assert is_valid == expected_result


def test_incorrect_signature():
    """
    Block with incorrect signature is not valid
    """

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
            'cfcba759125dfbaaefa627c4a41db4e5052705875d01228e5e280e13d403483fff495157b53192a6c1032ee815429f4979c0b4beb10d259fae3692123cf01f0d',
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
                        'amount': 4.25,
                        'recipient': '484b3176c63d5f37d808404af1a12c4b9649cd6f6769f35bdf5a816133623fbc'
                    },
                    {
                        'amount': 1,
                        'recipient': '5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8'
                    },
                    {
                        'amount': 4,
                        'recipient': 'ad1f8845c6a1abb6011a2a434a079a087c460657aad54329a84b406dce8bf314'
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
                    'recipient': '5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8'
                },
                {
                    'amount': 4,
                    'recipient': 'ad1f8845c6a1abb6011a2a434a079a087c460657aad54329a84b406dce8bf314'
                }
            ]
        },
        'signature': '85a255d720bf5897d65bad7ad410bab672d34bd0871ba20c1cb910a084d298e194fb86559eee093ab5d8c83dc7a785a235a3febb5d78f256066a8b70a271110a'
    }
    is_valid, account_balance = is_block_valid(block=block)
    assert not is_valid


def test_missing_transaction():
    """
    Block with missing transaction should be invalid
    """

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
                    'recipient': 'ad1f8845c6a1abb6011a2a434a079a087c460657aad54329a84b406dce8bf314'
                }
            ]
        },
        'signature': 'cfcba759125dfbaaefa627c4a41db4e5052705875d01228e5e280e13d403483fff495157b53192a6c1032ee815429f4979c0b4beb10d259fae3692123cf01f0d'
    }
    is_valid, account_balance = is_block_valid(block=block)
    assert not is_valid


def test_valid_block():
    """
    Valid block is validated correctly
    """

    block = {
        'account_number': '0cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb',
        'message': {
            'balance_key': '0cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb',
            'txs': [
                {
                    'amount': 4,
                    'recipient': '484b3176c63d5f37d808404af1a12c4b9649cd6f6769f35bdf5a816133623fbc'
                },
                {
                    'amount': 1,
                    'recipient': '5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8'
                },
                {
                    'amount': 4,
                    'recipient': 'ad1f8845c6a1abb6011a2a434a079a087c460657aad54329a84b406dce8bf314'
                }
            ]
        },
        'signature': '9c95931ff252b24d53ea899c0766f313675d05e0a522c81ef860415e7ebae88098f6f120ffb7dbe8f6acb3969aaab39be9bbb3eb6445f5f8d99b84a162107a0a'
    }
    is_valid, account_balance = is_block_valid(block=block)
    assert is_valid
