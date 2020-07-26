from django.core.cache import cache
from django.db.models import Q
from thenewboston.base_classes.connect_to_primary_validator import ConnectToPrimaryValidator
from thenewboston.utils.fields import standard_field_names
from thenewboston.utils.messages import get_message_hash

from v1.cache_tools.cache_keys import CONFIRMATION_BLOCK_QUEUE, HEAD_BLOCK_HASH
from v1.self_configurations.helpers.self_configuration import get_self_configuration
from v1.self_configurations.models.self_configuration import SelfConfiguration
from v1.tasks.confirmation_block_queue import process_confirmation_block_queue
from v1.tasks.sync import get_confirmation_block, populate_confirmation_block_queue
from v1.validators.models.validator import Validator

"""
python3 manage.py initialize_confirmation_validator

Notes:
- this should be ran after initialize_validator
- connects to the primary validator

Running this script will:
- connect to Validator and download config
- create a Validator object using config data
- set that Validator as the primary validator
"""


class Command(ConnectToPrimaryValidator):
    help = 'Initialize a confirmation validator and connect to the primary validator'

    def __init__(self):
        super().__init__()
        self.stdout.write(self.style.SUCCESS('Enter primary validator information'))

    def get_initial_block_identifier(self, primary_validator_config):
        """
        Return initial block identifier

        If seed_block_identifier, fetch related (seed) block and hash to get initial block identifier
        Otherwise, return root_account_file_hash
        """

        seed_block_identifier = primary_validator_config.get('seed_block_identifier')

        if not seed_block_identifier:
            self_configuration = get_self_configuration(exception_class=RuntimeError)
            root_account_file_hash = self_configuration.root_account_file_hash
            pv_root_account_file_hash = primary_validator_config.get('root_account_file_hash')

            if root_account_file_hash != pv_root_account_file_hash:
                self._error(
                    'SelfConfiguration.root_account_file_hash does not match primary validator root_account_file_hash'
                )
                self._error(f'SelfConfiguration: {root_account_file_hash}')
                self._error(f'Primary validator: {pv_root_account_file_hash}')
                raise RuntimeError()

            return root_account_file_hash

        address = self.get_primary_validator_address()
        confirmation_block = get_confirmation_block(address=address, block_identifier=seed_block_identifier)

        return get_message_hash(message=confirmation_block['message'])

    def set_primary_validator(self, primary_validator_config):
        """
        Set primary validator
        """

        validator_field_names = standard_field_names(Validator)
        validator_data = {k: v for k, v in primary_validator_config.items() if k in validator_field_names}

        Validator.objects.filter(
            Q(ip_address=validator_data.get('ip_address')) |
            Q(node_identifier=validator_data.get('node_identifier'))
        ).delete()

        validator = Validator.objects.create(
            **validator_data,
            trust=self.required_input['trust']
        )
        self_configuration = SelfConfiguration.objects.first()
        self_configuration.primary_validator = validator
        self_configuration.save()

        self.sync(primary_validator_config=primary_validator_config)

    def sync(self, *, primary_validator_config):
        """
        Sync with primary validator
        """

        initial_block_identifier = self.get_initial_block_identifier(primary_validator_config=primary_validator_config)

        cache.set(CONFIRMATION_BLOCK_QUEUE, {}, None)
        cache.set(HEAD_BLOCK_HASH, initial_block_identifier, None)

        self.stdout.write(self.style.SUCCESS('Adding blocks to CONFIRMATION_BLOCK_QUEUE...'))

        populate_confirmation_block_queue(
            address=self.get_primary_validator_address(),
            error_handler=self._error,
            initial_block_identifier=initial_block_identifier
        )
        process_confirmation_block_queue()
