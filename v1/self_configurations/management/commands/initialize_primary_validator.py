from django.core.management.base import BaseCommand, CommandError
from thenewboston.constants.network import VALIDATOR

from v1.self_configurations.models.self_configuration import SelfConfiguration
from v1.validators.models.validator import Validator

"""
python3 manage.py initialize_primary_validator
"""


class Command(BaseCommand):
    help = 'Initialize primary validator'

    def __init__(self):
        super().__init__()
        self.required_input = {
            'account_number': None,
            'default_transaction_fee': None,
            'head_hash': None,
            'ip_address': None,
            'network_identifier': None,
            'node_type': VALIDATOR,
            'port': None,
            'primary_validator': None,
            'protocol': None,
            'registration_fee': None,
            'root_account_file': None,
            'root_account_file_hash': None,
            'seed_hash': None,
            'version': None
        }

    @staticmethod
    def check_initialization_requirements():
        """
        Verify that no existing SelfConfiguration or Validator(s) already exist
        """

        if SelfConfiguration.objects.exists():
            raise CommandError('Unable to initialize with existing SelfConfiguration')

        if Validator.objects.exists():
            raise CommandError('Unable to initialize with existing Validator(s)')

    def get_account_number(self):
        """
        Get account number from user
        """

        while not self.required_input['account_number']:
            account_number = input('Enter account number: ')

            if account_number:
                self.required_input['account_number'] = account_number
                print(account_number)

    def handle(self, *args, **options):
        """
        Run script
        """

        print(options)
        self.check_initialization_requirements()

        # Input values
        self.get_account_number()

        self.stdout.write(self.style.SUCCESS('Nice'))
