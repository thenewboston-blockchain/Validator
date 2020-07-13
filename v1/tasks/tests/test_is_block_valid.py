from v1.tasks.block_queue import is_block_valid
from v1.test_tools.test_primary_validator import TestPrimaryValidator


class TestIsBlockValid(TestPrimaryValidator):

    def test_incorrect_amount(self):
        """
        Block with incorrect amount(s) is not valid
        - amount of 4.26 was changed from 4.25
        """

        data = [
            (-.23, False),
            (0.00, False),
            (4.24, False),
            (4.25, True),
            (4.26, False),
            (9.99, False),
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
                'signature': 'ac701d66f5063ea4fab9f8850270461267316f28b4fbf153af8bc3aaf9c3dc42088669501fde3815800de606462657d1c93f688fbb331070bc035019cba55d09'
            }
            is_valid, account_balance = is_block_valid(block=block)
            self.assertEqual(is_valid, expected_result)

    def test_incorrect_balance_key(self):
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
                'signature': 'ac701d66f5063ea4fab9f8850270461267316f28b4fbf153af8bc3aaf9c3dc42088669501fde3815800de606462657d1c93f688fbb331070bc035019cba55d09'
            }
            is_valid, account_balance = is_block_valid(block=block)
            self.assertEqual(is_valid, expected_result)

    def test_incorrect_signature(self):
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
                'ac701d66f5063ea4fab9f8850270461267316f28b4fbf153af8bc3aaf9c3dc42088669501fde3815800de606462657d1c93f688fbb331070bc035019cba55d09',
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
            self.assertEqual(is_valid, expected_result)

    def test_invalid_amount(self):
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
        self.assertFalse(is_valid)

    def test_missing_transaction(self):
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
            'signature': 'ac701d66f5063ea4fab9f8850270461267316f28b4fbf153af8bc3aaf9c3dc42088669501fde3815800de606462657d1c93f688fbb331070bc035019cba55d09'
        }
        is_valid, account_balance = is_block_valid(block=block)
        self.assertFalse(is_valid)

    def test_valid_block(self):
        """
        Valid block is validated correctly
        """

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
            'signature': 'ac701d66f5063ea4fab9f8850270461267316f28b4fbf153af8bc3aaf9c3dc42088669501fde3815800de606462657d1c93f688fbb331070bc035019cba55d09'
        }
        is_valid, account_balance = is_block_valid(block=block)
        self.assertTrue(is_valid)
