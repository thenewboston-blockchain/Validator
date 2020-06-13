import decimal
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import URLValidator, validate_ipv46_address
from thenewboston.constants.network import (
    HEAD_HASH_LENGTH,
    MIN_POINT_VALUE,
    PROTOCOL_LIST,
    VALIDATOR,
    VERIFY_KEY_LENGTH
)
from thenewboston.utils.files import get_file_hash, write_json
from thenewboston.utils.validators import validate_is_real_number

from v1.self_configurations.models.self_configuration import SelfConfiguration
from v1.validators.models.validator import Validator

"""
python3 manage.py initialize_primary_validator

Must handle both:
- branching from an existing network (primary validator candidate)
- network initialization (for testing/development)
"""

LOCAL_ROOT_ACCOUNT_FILE_PATH = os.path.join(settings.TMP_DIR, 'root_account_file.json')


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
            'port': None,
            'protocol': None,
            'registration_fee': None,
            'root_account_file': None,
            'root_account_file_hash': None,
            'seed_block_hash': None,
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

    @staticmethod
    def download_root_account_file(*, url, destination_file_path):
        """
        Download root account JSON file and save
        """

        print('Downloading file...')

        request = Request(url)
        response = urlopen(request)
        results = json.loads(response.read())
        write_json(destination_file_path, results)

    def get_fee(self, *, attribute_name, human_readable_name):
        """
        Validate fee
        - default_transaction_fee
        - registration_fee
        """

        valid = False

        while not valid:
            fee = input(f'Enter {human_readable_name} (required): ')

            if not fee:
                self._error(f'{attribute_name} required')
                continue

            is_valid_decimal, fee = self.validate_and_convert_to_decimal(fee)

            if not is_valid_decimal:
                continue

            try:
                validate_is_real_number(fee)
            except ValidationError:
                self._error('Value must be a real number')
                continue

            if fee < MIN_POINT_VALUE:
                self._error(f'Value can not be less than {MIN_POINT_VALUE:.16f}')
                continue

            self.required_input[attribute_name] = fee
            valid = True

    def get_ip_address(self):
        """
        Get IP address from user
        """

        valid = False

        while not valid:
            ip_address = input('Enter public IP address (required): ')

            if not ip_address:
                self._error('ip_address required')
                continue

            try:
                validate_ipv46_address(ip_address)
            except ValidationError:
                self._error('Enter a valid IPv4 or IPv6 address')
                continue

            self.required_input['ip_address'] = ip_address
            valid = True

    def get_port(self):
        """
        Get port from user
        """

        valid = False

        while not valid:
            port = input('Enter port: ')

            if not port:
                break

            try:
                port = int(port)
            except ValueError:
                self._error(f'{port} is not a valid integer')
                continue

            if port < 0:
                self._error(f'port can not be less than 0')
                continue

            if port > 65535:
                self._error(f'port can not be greater than 65535')
                continue

            self.required_input['port'] = port
            valid = True

    def get_protocol(self):
        """
        Get protocol from user
        """

        valid = False

        while not valid:
            protocol = input('Enter protocol (required): ')

            if not protocol:
                self._error('protocol required')
                continue

            if protocol not in PROTOCOL_LIST:
                self._error(f'protocol must be one of {PROTOCOL_LIST}')
                continue

            self.required_input['protocol'] = protocol
            valid = True

    def get_root_account_file(self):
        """
        Get root account file from user
        """

        valid = False

        while not valid:
            root_account_file = input('Enter root account file URL (required): ')

            if not root_account_file:
                self._error('root_account_file required')
                continue

            try:
                url_validator = URLValidator(schemes=['http', 'https'])
                url_validator(root_account_file)
            except ValidationError:
                self._error('Invalid URL')
                continue

            if Path(root_account_file).suffix != '.json':
                self._error('JSON file required')
                continue

            try:
                self.download_root_account_file(
                    url=root_account_file,
                    destination_file_path=LOCAL_ROOT_ACCOUNT_FILE_PATH
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error downloading {root_account_file}'))
                self.stdout.write(self.style.ERROR(e))

            file_hash = get_file_hash(LOCAL_ROOT_ACCOUNT_FILE_PATH)
            self.required_input.update({
                'head_hash': file_hash,
                'root_account_file': root_account_file,
                'root_account_file_hash': file_hash
            })
            valid = True

    def get_seed_block_hash(self):
        """
        Get seed block hash from user
        """

        valid = False

        while not valid:
            seed_block_hash = input('Enter seed block hash (required): ')

            if not seed_block_hash:
                self._error('seed_block_hash required')
                continue

            if seed_block_hash == '0':
                self.required_input['seed_block_hash'] = seed_block_hash
                break

            if len(seed_block_hash) != HEAD_HASH_LENGTH:
                self._error(
                    f'Invalid character length for seed_block_hash\n\n'
                    f'Enter a {HEAD_HASH_LENGTH} character hash value when branching from an existing network\n'
                    f'- recommended\n'
                    f'- set value to the hash of the last block that was used when root_account_file was generated\n'
                    f'- initializes this validator as a primary validator candidate\n\n'
                    f'Enter 0 if initializing a test network\n'
                    f'- not recommended\n'
                    f'- used for development'
                )
                continue

            self.required_input['seed_block_hash'] = seed_block_hash
            valid = True

    def get_verify_key(self, *, attribute_name, human_readable_name):
        """
        Validate verify key
        - account_number
        - network_identifier
        """

        valid = False

        while not valid:
            verify_key = input(f'Enter {human_readable_name} (required): ')

            if not verify_key:
                self._error(f'{attribute_name} required')
                continue

            if len(verify_key) != VERIFY_KEY_LENGTH:
                self._error(f'{attribute_name} must be {VERIFY_KEY_LENGTH} characters long')
                continue

            self.required_input[attribute_name] = verify_key
            valid = True

    def get_version_number(self):
        """
        Get version from user
        """

        max_length = 32
        valid = False

        while not valid:
            version = input('Enter version (required): ')

            if not version:
                self._error('version required')
                continue

            if len(version) > max_length:
                self._error(f'version must be less than or equal to {max_length} characters long')
                continue

            self.required_input['version'] = version
            valid = True

    def handle(self, *args, **options):
        """
        Run script
        """

        self.check_initialization_requirements()

        # Input values
        self.get_verify_key(
            attribute_name='network_identifier',
            human_readable_name='network identifier'
        )
        self.get_verify_key(
            attribute_name='account_number',
            human_readable_name='account number'
        )
        self.get_fee(
            attribute_name='default_transaction_fee',
            human_readable_name='default transaction fee'
        )
        self.get_fee(
            attribute_name='registration_fee',
            human_readable_name='registration fee'
        )
        self.get_root_account_file()
        self.get_seed_block_hash()
        self.get_protocol()
        self.get_ip_address()
        self.get_port()
        self.get_version_number()

        self.initialize_validator()

    def initialize_validator(self):
        """
        Create SelfConfiguration and Validator objects
        """

        validator = Validator.objects.create(
            **self.required_input,
            trust=100
        )
        SelfConfiguration.objects.create(
            **self.required_input,
            node_type=VALIDATOR,
            primary_validator=validator
        )
        self.stdout.write(self.style.SUCCESS('Initialization complete'))

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
