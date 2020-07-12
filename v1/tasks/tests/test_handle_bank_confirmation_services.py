from v1.self_configurations.helpers.self_configuration import get_self_configuration
from v1.tasks.confirmation_blocks import handle_bank_confirmation_services
from v1.test_tools.test_confirmation_validator import TestConfirmationValidator


class TestHandleConfirmationServices(TestConfirmationValidator):

    def test_seconds_purchased(self):
        """
        Test that the correct amount of time is purchased
        """

        self_configuration = get_self_configuration(exception_class=RuntimeError)

        data = [
            (10, 86400),
            (20, 172800),
        ]

        for amount, expected_result in data:
            block = {
                'account_number': '5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8',
                'message': {
                    'balance_key': '2e5fa4f3bfce4fba6c360bb45cbea2b0af6ed99349cb81b1028ffac6176b2cc5',
                    'txs': [
                        {
                            'amount': amount,
                            'recipient': self_configuration.account_number
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
                'signature': 'ceb184bc5678b57d82bf6a56df09dd50ed2a26a0e3037b7c0ec43aa07863786e564ebdc155ab3b083f580abc6538a24dcb4278dae22fbb8055e38c9941b85901'
            }

            seconds_purchased = handle_bank_confirmation_services(block=block, self_configuration=self_configuration)
            self.assertEqual(seconds_purchased, expected_result)
