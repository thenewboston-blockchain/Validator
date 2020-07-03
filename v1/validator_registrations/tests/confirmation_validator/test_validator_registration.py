from rest_framework import status

from v1.test_tools.test_confirmation_validator import TestConfirmationValidator


class TestValidatorRegistration(TestConfirmationValidator):

    def test_create_validator_registration_with_confirmation_validator(self):
        """
        Validate creation of validator registration with confirmation validator
        """

        payload = {
            "message": {
                "block": {
                    "account_number": "0cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb",
                    "message": {
                        "balance_key": "0cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb",
                        "txs": [
                            {
                                "amount": 8,
                                "recipient": "ad1f8845c6a1abb6011a2a434a079a087c460657aad54329a84b406dce8bf314"
                            }
                        ]
                    },
                    "signature": "219d60986e0e0b2524ff565157c3f9e776af0c2aeaba2c4594c3082d8471c0d3adf15b57cb28e4400e85e3084d23c84db0840e99956e7723b3063d42ff96b80f"
                },
                "pk": "16e1323c-b465-4f54-b5a0-a282bf80e756",
                "source_ip_address": "192.168.1.232",
                "source_node_identifier": "59479a31c3b91d96bb7a0b3e07f18d4bf301f1bb0bde05f8d36d9611dcbe7cbf",
                "source_port": 8000,
                "source_protocol": "http",
                "target_ip_address": "192.168.1.65",
                "target_node_identifier": "3afdf37573f1a511def0bd85553404b7091a76bcd79cdcebba1310527b167521",
                "target_port": 8000,
                "target_protocol": "http"
            },
            "node_identifier": "59479a31c3b91d96bb7a0b3e07f18d4bf301f1bb0bde05f8d36d9611dcbe7cbf",
            "signature": "1f901fd3fa3ea47d1f89b5837ee6d67a12e8c6687c65ce9d03b51bd9a2addba53bbd19c5cd831b3eee0cabfd55adbd9a179869baf11c300338ef18d54dd0fa04"
        }
        self.validate_post('/validator_registrations', payload, status.HTTP_201_CREATED)
