import logging
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management import CommandParser
from django.core.validators import URLValidator
from django.db.models import Q
from sentry_sdk import capture_exception
from thenewboston.argparser.validators import str_length_validator, url_validator
from thenewboston.base_classes.initialize_node import InitializeNode
from thenewboston.constants.network import (
    BLOCK_IDENTIFIER_LENGTH,
    CONFIRMATION_VALIDATOR,
    HEAD_HASH_LENGTH,
    PRIMARY_VALIDATOR
)
from thenewboston.utils.files import get_file_hash
from thenewboston.utils.format import format_address

from v1.cache_tools.helpers import rebuild_cache
from v1.cache_tools.valid_confirmation_blocks import delete_all_valid_confirmation_blocks
from v1.self_configurations.helpers.self_configuration import get_root_account_file_url
from v1.self_configurations.models.self_configuration import SelfConfiguration
from v1.sync.helpers import download_root_account_file, sync_accounts_table_to_root_account_file
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

logger = logging.getLogger('thenewboston')


class Command(InitializeNode):
    help = 'Initialize validator'  # noqa: A003

    def __init__(self, *args, **kwargs):
        """Inits Command class"""
        super().__init__(*args, **kwargs)

        self.required_input = {
            'account_number': None,
            'daily_confirmation_rate': None,
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
            'version': None,
        }

    def add_arguments(self, parser: CommandParser):
        """Additional custom arguments"""
        super(Command, self).add_arguments(parser)
        parser.add_argument('--node_type', choices=[CONFIRMATION_VALIDATOR, PRIMARY_VALIDATOR])
        parser.add_argument('--seed_block_identifier', type=str_length_validator(length=BLOCK_IDENTIFIER_LENGTH))
        parser.add_argument('--head_block_hash', type=str_length_validator(length=HEAD_HASH_LENGTH))
        parser.add_argument('--root_account_file', type=url_validator(suffix='.json'))
        parser.add_argument('--daily_confirmation_rate', type=int)

    def get_head_block_hash(self, value=None):
        """Get head block hash"""
        if not self.required_input['seed_block_identifier']:
            return

        valid = False

        while not valid:
            if self.unattended:
                head_block_hash = value
            else:
                head_block_hash = input('Enter head_block_hash: ')

            if not head_block_hash:
                break

            if len(head_block_hash) != HEAD_HASH_LENGTH:
                self._error(f'head_block_hash must be {HEAD_HASH_LENGTH} characters long')
                continue

            self.required_input['head_block_hash'] = head_block_hash
            valid = True

    def get_node_type(self, value=None):
        """Get node type"""
        valid = False

        while not valid:
            if self.unattended:
                node_type = value
            else:
                node_type = input('Enter node_type (required): ')

            if not node_type:
                continue

            if node_type not in [CONFIRMATION_VALIDATOR, PRIMARY_VALIDATOR]:
                self._error(f'node_type must be one of {CONFIRMATION_VALIDATOR} or {PRIMARY_VALIDATOR}')
                continue

            self.required_input['node_type'] = node_type
            valid = True

    def get_root_account_file(self, value=None):
        """Get root account file from user"""
        valid = False

        while not valid:
            if self.unattended:
                root_account_file = value
            else:
                root_account_file = input('Enter root account file URL (required): ')

            if not root_account_file:
                self._error('root_account_file required')
                continue

            try:
                validator = URLValidator(schemes=['http', 'https'])
                validator(root_account_file)
            except ValidationError:
                self._error('Invalid URL')
                continue

            if Path(root_account_file).suffix != '.json':
                self._error('JSON file required')
                continue

            try:
                download_root_account_file(url=root_account_file)
            except Exception as e:
                capture_exception(e)
                logger.exception(e)
                self.stdout.write(self.style.ERROR(f'Error downloading {root_account_file}'))
                self.stdout.write(self.style.ERROR(e))
                continue

            file_hash = get_file_hash(settings.ROOT_ACCOUNT_FILE_PATH)

            if not self.required_input['head_block_hash']:
                self.required_input['head_block_hash'] = file_hash

            self_address = format_address(
                ip_address=self.required_input.get('ip_address'),
                port=self.required_input.get('port'),
                protocol=self.required_input.get('protocol'),
            )
            root_account_file = get_root_account_file_url(address=self_address)

            self.required_input.update({
                'root_account_file': root_account_file,
                'root_account_file_hash': file_hash
            })
            valid = True

    def get_seed_block_identifier(self, value=None):
        """Get seed block identifier from user"""
        valid = False

        while not valid:
            if self.unattended:
                seed_block_identifier = value
            else:
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
        """Run script"""
        # Input values
        self.get_verify_key(
            attribute_name='node_identifier',
            human_readable_name='node identifier',
            value=options.get('node_identifier')
        )
        self.get_verify_key(
            attribute_name='account_number',
            human_readable_name='account number',
            value=options.get('account_number')
        )
        self.get_fee(
            attribute_name='default_transaction_fee',
            human_readable_name='default transaction fee',
            value=options.get('default_transaction_fee')
        )
        self.get_fee(
            attribute_name='daily_confirmation_rate',
            human_readable_name='daily confirmation rate',
            value=options.get('daily_confirmation_rate')
        )
        self.get_node_type(value=options.get('node_type'))
        self.get_seed_block_identifier(value=options.get('seed_block_identifier'))
        self.get_head_block_hash(value=options.get('head_block_hash'))
        self.get_protocol(value=options.get('protocol'))
        self.get_ip_address(value=options.get('ip_address'))
        self.get_port(value=options.get('port'))
        self.get_root_account_file(value=options.get('root_account_file'))
        self.get_version_number(value=options.get('version_number'))

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
            Q(ip_address=self.required_input['ip_address']) | Q(node_identifier=self.required_input['node_identifier'])
        ).delete()

        # Create SelfConfiguration and related Validator objects
        SelfConfiguration.objects.create(
            **self.required_input,
            node_type=node_type
        )
        sync_accounts_table_to_root_account_file()

        # Rebuild cache
        rebuild_cache(head_block_hash=head_block_hash)
        delete_all_valid_confirmation_blocks()

        self.stdout.write(self.style.SUCCESS('Validator initialization complete'))
