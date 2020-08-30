import logging

from django.core.cache import cache
from django.db.models import Q
from thenewboston.utils.format import format_address
from thenewboston.utils.network import fetch

from v1.cache_tools.cache_keys import CONFIRMATION_BLOCK_QUEUE, HEAD_BLOCK_HASH
from v1.self_configurations.helpers.self_configuration import get_self_configuration
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


def get_trust(*, config):
    """
    Return trust level for existing validator
    """

    validator = Validator.objects.filter(
        ip_address=config.get('ip_address'),
        node_identifier=config.get('node_identifier')
    ).first()

    if validator:
        return validator.trust

    return 0


def remove_existing_validators(*, config):
    """
    Remove any existing validators
    """

    Validator.objects.filter(
        Q(ip_address=config.get('ip_address')) |
        Q(node_identifier=config.get('node_identifier'))
    ).delete()


def set_primary_validator(*, validator):
    """
    Set validator as primary validator
    """

    self_configuration = get_self_configuration(exception_class=RuntimeError)
    self_configuration.primary_validator = validator
    self_configuration.save()

    sync_blockchains(primary_validator=validator)


def sync_blockchains(*, primary_validator):
    """
    Sync blockchains with the primary validator

    Starting confirmation block order of operations:

    1. self HEAD_BLOCK_HASH - attempt to append blocks onto this nodes existing blockchain

    2. PV seed_block_identifier - if PV does not have block matching the self HEAD_BLOCK_HASH, sync from the
    PVs seed_block_identifier

    3. PV root_account_file_hash - if no PV seed_block_identifier exists, that indicates that the PV has began as a
    brand new network and we therefore must sync from the root_account_file_hash
    """

    cache.set(CONFIRMATION_BLOCK_QUEUE, {}, None)
    head_block_hash = cache.get(HEAD_BLOCK_HASH)


def sync_with_primary_validator(*, ip_address, port, protocol, trust=None):
    """
    Sync with primary validator
    """

    config = fetch_config(
        ip_address=ip_address,
        port=port,
        protocol=protocol
    )

    if trust is None:
        trust = get_trust(config=config)

    remove_existing_validators(config=config)
    serializer = PrimaryValidatorSyncSerializer(data=config)

    if serializer.is_valid():
        validator = serializer.save()
        validator.trust = trust
        validator.save()
        return

    logger.exception(serializer.errors)
    raise RuntimeError(serializer.errors)
