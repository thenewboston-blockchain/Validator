from thenewboston_validator.self_configurations.helpers.self_configuration import get_root_account_file_url
from ..sync_with_primary_validator import sync_from_primary_validators_initial_block


def test_sync_with_primary_validator(confirmation_validator_configuration):
    self_configuration = confirmation_validator_configuration
    primary_validator = self_configuration.primary_validator

    sync_from_primary_validators_initial_block(
        primary_validator=primary_validator,
    )
    self_configuration.refresh_from_db()

    assert self_configuration.root_account_file == get_root_account_file_url()
