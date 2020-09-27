from django.conf import settings
from django.core.files.storage import default_storage
from thenewboston.utils.format import format_address

from ..sync_with_primary_validator import sync_from_primary_validators_initial_block


def test_sync_with_primary_validator(confirmation_validator_configuration):
    self_configuration = confirmation_validator_configuration
    self_address = format_address(
        ip_address=self_configuration.ip_address,
        port=self_configuration.port,
        protocol=self_configuration.protocol,
    )
    primary_validator = self_configuration.primary_validator

    sync_from_primary_validators_initial_block(
        primary_validator=primary_validator,
    )
    self_configuration.refresh_from_db()

    assert (
        self_configuration.root_account_file ==
        self_address + default_storage.url(settings.ROOT_ACCOUNT_FILE_PATH)
    )
