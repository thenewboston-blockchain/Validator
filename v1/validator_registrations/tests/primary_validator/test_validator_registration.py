from rest_framework import status

from v1.test_tools.test_primary_validator import TestPrimaryValidator
from v1.validator_registrations.models.validator_registration import ValidatorRegistration
from v1.validators.models.validator import Validator


class TestValidatorRegistration(TestPrimaryValidator):

    def test_create_validator_registration_with_primary_validator(self):
        """
        Validate creation of validator registration with primary validator
        """

        Validator.objects.all().delete()
        ValidatorRegistration.objects.all().delete()

        payload = {
            'message': {
                'block': {
                    'account_number': '5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8',
                    'message': {
                        'balance_key': '5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8',
                        'txs': [
                            {
                                'amount': 8,
                                'recipient': 'ad1f8845c6a1abb6011a2a434a079a087c460657aad54329a84b406dce8bf314'
                            }
                        ]
                    },
                    'signature': 'a341eb2d678df410fb110760fd2c77c5969975d4fcba9a3846d9f11dfb43151bc23a157c26dd29163f061697806bc2b75d74a300ed6ba1a504ae2de6013d8c0f'
                },
                'ip_address': '192.168.1.232',
                'pk': '3b4f6ce5-1492-4228-925a-d2abf0361884',
                'port': 8000,
                'protocol': 'http',
                'validator_node_identifier': '3afdf37573f1a511def0bd85553404b7091a76bcd79cdcebba1310527b167521',
                'version': 'v1.0'
            },
            'node_identifier': 'd5356888dc9303e44ce52b1e06c3165a7759b9df1e6a6dfbd33ee1c3df1ab4d1',
            'signature': '601e227ded908d7decbf1682761bf305f00c504288a6bc53429abc43396f4428406f7fd26ae04e1e5e1238bbc51c759a07c9ccc6683d31b323e72a5310612006'
        }
        self.validate_post('/validator_registrations', payload, status.HTTP_201_CREATED)
