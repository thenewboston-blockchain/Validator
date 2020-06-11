import decimal

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from thenewboston.constants.network import MIN_POINT_VALUE, VALIDATOR, VERIFY_KEY_LENGTH
from thenewboston.utils.validators import validate_is_real_number

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

    def _error(self, message):
        """
        Display error message string in console
        """

        self.stdout.write(self.style.ERROR(message))

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

        valid = False

        while not valid:
            account_number = input('Enter account number (required): ')

            if not account_number:
                self._error('account_number required')
                continue

            if len(account_number) != VERIFY_KEY_LENGTH:
                self._error(f'account_number must be {VERIFY_KEY_LENGTH} characters long')
                continue

            self.required_input['account_number'] = account_number
            valid = True

    def get_default_transaction_fee(self):
        """
        Get default transaction fee from user
        """

        valid = False

        while not valid:
            default_transaction_fee = input('Enter default transaction fee (required): ')

            if not default_transaction_fee:
                self._error('default_transaction_fee required')
                continue

            is_valid_decimal, default_transaction_fee = self.validate_and_convert_to_decimal(default_transaction_fee)

            if not is_valid_decimal:
                continue

            try:
                validate_is_real_number(default_transaction_fee)
            except ValidationError:
                self._error('Value must be a real number')
                continue

            if default_transaction_fee < MIN_POINT_VALUE:
                self._error(f'Value can not be less than {MIN_POINT_VALUE:.16f}')
                continue

            self.required_input['default_transaction_fee'] = default_transaction_fee
            valid = True

    def handle(self, *args, **options):
        """
        Run script
        """

        self.check_initialization_requirements()

        # Input values
        self.get_account_number()
        self.get_default_transaction_fee()

        self.stdout.write(self.style.SUCCESS('Nice'))

    def validate_and_convert_to_decimal(self, value):
        """
        Validate that given value can be converted to Decimal value
        Returns: is_valid (bool), decimal_value (Decimal)

        Must return is_valid flag along with decimal_value to allow for proper validation of valid falsy value (0.0)
        """

        try:
            value = decimal.Decimal(value)
        except decimal.InvalidOperation:
            self._error(f'Can not convert {value} to a decimal')
            return False, None

        return True, value
