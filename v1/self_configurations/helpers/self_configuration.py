from django.conf import settings
from django.core.files.storage import default_storage
from thenewboston.utils.format import format_address

from ..models.self_configuration import SelfConfiguration


def get_primary_validator():
    """Return primary validator"""
    # TODO: This should be hitting the cache

    self_configuration = get_self_configuration(exception_class=RuntimeError)
    return self_configuration.primary_validator


def get_root_account_file_url(*, address=None):
    """Return root account file URL"""
    if not address:
        self_configuration = get_self_configuration(exception_class=RuntimeError)

        address = format_address(
            ip_address=self_configuration.ip_address,
            port=self_configuration.port,
            protocol=self_configuration.protocol,
        )

    return address + default_storage.url(settings.ROOT_ACCOUNT_FILE_PATH)


def get_self_configuration(*, exception_class):
    """Return self configuration"""
    self_configuration = SelfConfiguration.objects.first()

    if not self_configuration:
        raise exception_class('No self configuration')

    return self_configuration
