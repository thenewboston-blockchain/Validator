from django.db.models import Q
from thenewboston.base_classes.fetch_primary_validator_config import FetchPrimaryValidatorConfig
from thenewboston.utils.fields import standard_field_names

from v1.connection_requests.helpers.connect import connect_to_primary_validator
from v1.self_configurations.models.self_configuration import SelfConfiguration
from v1.sync.manager import sync_with_primary_validator
from v1.validators.models.validator import Validator

"""
python3 manage.py initialize_confirmation_validator

Notes:
- this should be ran after initialize_validator

Running this script will:
- fetch config data from primary validator
- create a Validator instance using config data
- set that Validator as this nodes primary validator
- connect to the primary validator
- send a request to the primary validator for any missing historical confirmation blocks
"""


class Command(FetchPrimaryValidatorConfig):
    help = 'Fetch config from PV, create related Validator, set that Validator as the primary validator'

    def __init__(self):
        super().__init__()
        self.stdout.write(self.style.SUCCESS('Enter primary validator information'))

    def handle_primary_validator_config(self, primary_validator_config):
        """
        Create a Validator instance using the primary_validator_config
        Set that Validator as this nodes primary validator
        Connect to the primary validator
        Synchronize blockchains with the primary validator
        """

        validator_field_names = standard_field_names(Validator)
        validator_data = {k: v for k, v in primary_validator_config.items() if k in validator_field_names}

        Validator.objects.filter(
            Q(ip_address=validator_data.get('ip_address')) |
            Q(node_identifier=validator_data.get('node_identifier'))
        ).delete()

        primary_validator = Validator.objects.create(
            **validator_data,
            trust=self.required_input['trust']
        )
        self_configuration = SelfConfiguration.objects.first()
        self_configuration.primary_validator = primary_validator
        self_configuration.save()

        try:
            self.stdout.write(self.style.SUCCESS('Connecting to primary validator...'))
            connect_to_primary_validator(primary_validator=primary_validator)
        except Exception as e:
            self._error(f'Connection failed: {e}')
            return

        self.stdout.write(self.style.SUCCESS('Syncing with primary validator...'))
        sync_with_primary_validator(
            ip_address=primary_validator.ip_address,
            port=primary_validator.port,
            protocol=primary_validator.protocol,
            trust=primary_validator.trust
        )
