from thenewboston.base_classes.fetch_primary_validator_config import FetchPrimaryValidatorConfig

from thenewboston_validator.tasks.sync_with_primary_validator import sync_with_primary_validator

"""
python3 manage.py set_primary_validator

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
    help = 'Fetch config from PV, create related Validator, set that Validator as the primary validator'  # noqa: A003

    def __init__(self, *args, **kwargs):
        """Inits Command class"""
        super().__init__(*args, **kwargs)
        if not self.unattended:
            self.stdout.write(self.style.SUCCESS('Enter primary validator information'))

    def handle_primary_validator_config(self, primary_validator_config):
        """Sync with primary validator"""
        self.stdout.write(self.style.SUCCESS('Syncing with primary validator...'))
        sync_with_primary_validator(
            config=primary_validator_config,
            trust=self.required_input['trust']
        )
