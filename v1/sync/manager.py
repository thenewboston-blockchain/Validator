import logging

from django.db.models import Q
from thenewboston.utils.format import format_address
from thenewboston.utils.network import fetch

from v1.validators.models.validator import Validator
from .serializers import PrimaryValidatorSyncSerializer

logger = logging.getLogger('thenewboston')


def fetch_config(*, ip_address, port, protocol):
    """
    Return config
    """

    address = format_address(
        ip_address=ip_address,
        port=port,
        protocol=protocol
    )
    url = f'{address}/config'

    try:
        results = fetch(url=url, headers={})
        return results
    except Exception as e:
        logger.exception(e)
        raise RuntimeError(e)


def remove_existing_validators(*, primary_validator_config):
    """
    Remove any existing validators
    """

    Validator.objects.filter(
        Q(ip_address=primary_validator_config.get('ip_address')) |
        Q(node_identifier=primary_validator_config.get('node_identifier'))
    ).delete()


def sync_with_primary_validator(*, ip_address, port, protocol, trust=0):
    """
    Sync with primary validator
    """

    primary_validator_config = fetch_config(
        ip_address=ip_address,
        port=port,
        protocol=protocol
    )

    serializer = PrimaryValidatorSyncSerializer(data=primary_validator_config)

    if serializer.is_valid():
        validator = serializer.save()
        validator.trust = trust
        validator.save()
        return

    logger.exception(serializer.errors)
    raise RuntimeError(serializer.errors)
