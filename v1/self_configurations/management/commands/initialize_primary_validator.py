import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from thenewboston.base_classes.initialize_node import InitializeNode
from thenewboston.constants.network import HEAD_HASH_LENGTH, VALIDATOR
from thenewboston.utils.files import get_file_hash, read_json, write_json

from v1.accounts.models.account import Account
from v1.cache_tools.helpers import rebuild_cache
from v1.self_configurations.models.self_configuration import SelfConfiguration
from v1.validators.models.validator import Validator

"""
python3 manage.py initialize_primary_validator

Running this script will:
- delete existing SelfConfiguration and related Validator objects
- create SelfConfiguration and related Validator objects
- create Account objects based on downloaded root_account_file
- rebuild cache

Must handle both:
- branching from an existing network (primary validator candidate)
- network initialization (for testing/development)
"""

LOCAL_ROOT_ACCOUNT_FILE_PATH = os.path.join(settings.TMP_DIR, 'root_account_file.json')


class Command(InitializeNode):
    help = 'Initialize primary validator'

    def __init__(self):
        super().__init__()

        self.head_block_hash = None
        self.required_input = {
            'account_number': None,
            'default_transaction_fee': None,
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
            self.head_block_hash = file_hash
            self.required_input.update({
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

    def handle(self, *args, **options):
        """
        Run script
        """

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

    @staticmethod
    def initialize_accounts():
        """
        Create Account objects
        """

        Account.objects.all().delete()
        account_data = read_json(LOCAL_ROOT_ACCOUNT_FILE_PATH)
        accounts = [
            Account(
                account_number=k,
                balance=v['balance'],
                balance_lock=v['balance_lock']
            ) for k, v in account_data.items()
        ]
        Account.objects.bulk_create(accounts)

    def initialize_validator(self):
        """
        Process to initialize validator:
        - delete existing SelfConfiguration and related Validator objects
        - create SelfConfiguration and related Validator objects
        - create Account objects based on downloaded root_account_file
        - rebuild cache
        """

        # Delete existing SelfConfiguration and related Validator objects
        SelfConfiguration.objects.all().delete()
        Validator.objects.filter(ip_address=self.required_input['ip_address']).delete()

        # Create SelfConfiguration and related Validator objects
        validator = Validator.objects.create(
            **self.required_input,
            trust=100
        )
        SelfConfiguration.objects.create(
            **self.required_input,
            node_type=VALIDATOR,
            primary_validator=validator
        )
        self.initialize_accounts()

        # Rebuild cache
        rebuild_cache(head_block_hash=self.head_block_hash)

        self.stdout.write(self.style.SUCCESS('Primary validator initialization complete'))
