from rest_framework import status

from v1.test_tools.test_confirmation_validator import TestConfirmationValidator


class TestValidatorRegistration(TestConfirmationValidator):

    def test_create_validator_registration_with_confirmation_validator(self):
        """
        Validate creation of validator registration with confirmation validator
        """

        payload = {
            'message': {
                'block': {
                    'account_number': '5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8',
                    'message': {
                        'balance_key': '5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8',
                        'txs': [
                            {
                                'amount': 8,
                                'recipient': '4d2ec91f37bc553bc538e91195669b666e26b2ea3e4e31507e38102a758d4f86'
                            },
                            {
                                'amount': 8,
                                'recipient': 'ad1f8845c6a1abb6011a2a434a079a087c460657aad54329a84b406dce8bf314'
                            }
                        ]
                    },
                    'signature': '826a52ff33a0144013cfc6503c08ad5abe95e42ed783d8f5d1c0980f0e43cfaabc19211546a4e3ef607f1ad6d3a0a714b671f378ae597722e66171f2b00f960c'
                },
                'ip_address': '192.168.1.232',
                'pk': '25ae1ca4-57a7-4740-82bc-76e797079d64',
                'port': 8000,
                'protocol': 'http',
                'validator_node_identifier': '3afdf37573f1a511def0bd85553404b7091a76bcd79cdcebba1310527b167521',
                'version': 'v1.0'
            },
            'node_identifier': 'd5356888dc9303e44ce52b1e06c3165a7759b9df1e6a6dfbd33ee1c3df1ab4d1',
            'signature': '59d2f15f67293a0769e03de94d2d5a0be8821607899b1a8e245e08f47e3b2586aa292ec5627c8da940f5723098cf6094483d40a86a48a42d0cfef924f5c9d60b'
        }
        self.validate_post('/validator_registrations', payload, status.HTTP_201_CREATED)
