import json
import logging
import os
from pathlib import Path
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db.models import Q
from thenewboston.base_classes.initialize_node import InitializeNode
from thenewboston.constants.network import (
    BLOCK_IDENTIFIER_LENGTH,
    CONFIRMATION_VALIDATOR,
    HEAD_HASH_LENGTH,
    PRIMARY_VALIDATOR
)
from thenewboston.utils.files import get_file_hash, read_json, write_json

from v1.accounts.models.account import Account
from v1.cache_tools.helpers import rebuild_cache
from v1.self_configurations.models.self_configuration import SelfConfiguration
from v1.validators.models.validator import Validator

"""
python3 manage.py initialize_validator

Prerequisites:
- python3 manage.py makemigrations
- python3 manage.py migrate
- python3 manage.py createsuperuser (optional)

Running this script will:
- delete existing SelfConfiguration and related Validator objects
- create SelfConfiguration and related Validator objects
- create Account objects based on downloaded root_account_file
- rebuild cache
"""

LOCAL_ROOT_ACCOUNT_FILE_PATH = os.path.join(settings.TMP_DIR, 'root_account_file.json')

logger = logging.getLogger('thenewboston')


class Command(InitializeNode):
    help = 'Initialize validator'

    def __init__(self):
        super().__init__()

        self.required_input = {
            'account_number': None,
            'default_transaction_fee': None,
            'head_block_hash': None,
            'ip_address': None,
            'node_identifier': None,
            'node_type': None,
            'port': None,
            'protocol': None,
            'root_account_file': None,
            'root_account_file_hash': None,
            'seed_block_identifier': None,
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

    def get_head_block_hash(self):
        """
        Get head block hash
        """

        if not self.required_input['seed_block_identifier']:
            return

        valid = False

        while not valid:
            head_block_hash = input('Enter head_block_hash: ')

            if not head_block_hash:
                break

            if len(head_block_hash) != HEAD_HASH_LENGTH:
                self._error(f'head_block_hash must be {HEAD_HASH_LENGTH} characters long')
                continue

            self.required_input['head_block_hash'] = head_block_hash
            valid = True

    def get_node_type(self):
        """
        Get node type
        """

        valid = False

        while not valid:
            node_type = input('Enter node_type (required): ')

            if not node_type:
                continue

            if node_type not in [CONFIRMATION_VALIDATOR, PRIMARY_VALIDATOR]:
                self._error(f'node_type must be one of {CONFIRMATION_VALIDATOR} or {PRIMARY_VALIDATOR}')
                continue

            self.required_input['node_type'] = node_type
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
                logger.exception(e)
                self.stdout.write(self.style.ERROR(f'Error downloading {root_account_file}'))
                self.stdout.write(self.style.ERROR(e))

            file_hash = get_file_hash(LOCAL_ROOT_ACCOUNT_FILE_PATH)

            if not self.required_input['head_block_hash']:
                self.required_input['head_block_hash'] = file_hash

            self.required_input.update({
                'root_account_file': root_account_file,
                'root_account_file_hash': file_hash
            })
            valid = True

    def get_seed_block_identifier(self):
        """
        Get seed block identifier from user
        """

        valid = False

        while not valid:
            seed_block_identifier = input('Enter seed block identifier: ')

            if not seed_block_identifier:
                self.required_input['seed_block_identifier'] = ''
                break

            if len(seed_block_identifier) != BLOCK_IDENTIFIER_LENGTH:
                self._error(
                    f'Invalid character length for seed_block_identifier\n\n'
                    f'Enter a {BLOCK_IDENTIFIER_LENGTH} character value when branching from an existing network\n'
                    f'- recommended\n'
                    f'- set value to the identifier of the last block used when root_account_file was generated\n\n'
                    f'Enter nothing if initializing a test network\n'
                    f'- not recommended\n'
                    f'- used for development'
                )
                continue

            self.required_input['seed_block_identifier'] = seed_block_identifier
            valid = True

    def handle(self, *args, **options):
        """
        Run script
        """

        # Input values
        self.get_verify_key(
            attribute_name='node_identifier',
            human_readable_name='node identifier'
        )
        self.get_verify_key(
            attribute_name='account_number',
            human_readable_name='account number'
        )
        self.get_fee(
            attribute_name='default_transaction_fee',
            human_readable_name='default transaction fee'
        )
        self.get_node_type()
        self.get_seed_block_identifier()
        self.get_head_block_hash()
        self.get_root_account_file()
        self.get_protocol()
        self.get_ip_address()
        self.get_port()
        self.get_version_number()

        self.initialize_validator()

    def initialize_validator(self):
        """
        Process to initialize validator:
        - delete existing SelfConfiguration and related Validator objects
        - create SelfConfiguration and related Validator objects
        - create Account objects based on downloaded root_account_file
        - rebuild cache
        """

        head_block_hash = self.required_input.pop('head_block_hash')
        node_type = self.required_input.pop('node_type')

        # Delete existing SelfConfiguration and related Validator objects
        SelfConfiguration.objects.all().delete()
        Validator.objects.filter(
            Q(ip_address=self.required_input['ip_address']) |
            Q(node_identifier=self.required_input['node_identifier'])
        ).delete()

        # Create SelfConfiguration and related Validator objects
        SelfConfiguration.objects.create(
            **self.required_input,
            node_type=node_type
        )
        self.update_accounts_table()

        # Rebuild cache
        rebuild_cache(head_block_hash=head_block_hash)

        self.stdout.write(self.style.SUCCESS('Validator initialization complete'))

    @staticmethod
    def update_accounts_table():
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
