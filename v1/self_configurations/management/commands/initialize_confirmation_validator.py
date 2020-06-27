from django.db.models import Q
from thenewboston.base_classes.connect_to_primary_validator import ConnectToPrimaryValidator
from thenewboston.utils.fields import standard_field_names
from thenewboston.utils.network import fetch

from v1.self_configurations.models.self_configuration import SelfConfiguration
from v1.tasks.blocks import get_message_hash
from v1.validators.models.validator import Validator

"""
python3 manage.py initialize_confirmation_validator

Running this script will:
- connect to Validator and download config
- create a Validator object using config data
- set that Validator as the primary validator
"""


class Command(ConnectToPrimaryValidator):
    help = 'Connect to primary validator'

    def get_confirmation_block(self, *, block_identifier):
        """
        Return confirmation block chain segment
        """

        address = self.get_primary_validator_address()
        url = f'{address}/confirmation_blocks/{block_identifier}'
        results = fetch(url=url, headers={})
        return results

    def get_confirmation_block_chain_segment(self, *, block_identifier):
        """
        Return confirmation block chain segment
        """

        address = self.get_primary_validator_address()
        url = f'{address}/confirmation_block_chain_segment/{block_identifier}'
        results = fetch(url=url, headers={})
        return results

    def get_initial_block_identifier(self, validator_config):
        """
        Return initial block identifier

        If seed_block_identifier, fetch related (seed) block and hash to get initial block identifier
        Otherwise, return root_account_file_hash
        """

        seed_block_identifier = validator_config.get('seed_block_identifier')

        if not seed_block_identifier:
            return validator_config.get('root_account_file_hash')

        confirmation_block = self.get_confirmation_block(block_identifier=seed_block_identifier)

        return get_message_hash(message=confirmation_block['message'])

    def set_primary_validator(self, validator_config):
        """
        Set primary validator
        """

        validator_field_names = standard_field_names(Validator)
        validator_data = {k: v for k, v in validator_config.items() if k in validator_field_names}

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

        initial_block_identifier = self.get_initial_block_identifier(validator_config=validator_config)
        print(initial_block_identifier)
