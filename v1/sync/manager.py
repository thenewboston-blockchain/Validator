import logging

from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from thenewboston.utils.fields import standard_field_names
from thenewboston.utils.files import get_file_hash
from thenewboston.utils.format import format_address
from thenewboston.utils.network import fetch

from v1.cache_tools.cache_keys import CONFIRMATION_BLOCK_QUEUE, HEAD_BLOCK_HASH
from v1.cache_tools.helpers import rebuild_cache
from v1.connection_requests.helpers.connect import connect_to_primary_validator
from v1.self_configurations.helpers.self_configuration import get_self_configuration
from v1.validators.models.validator import Validator
from .helpers import download_root_account_file, sync_accounts_table_to_root_account_file
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


def fetch_confirmation_block(*, primary_validator, block_identifier):
    """
    Return confirmation block
    """

    address = format_address(
        ip_address=primary_validator.ip_address,
        port=primary_validator.port,
        protocol=primary_validator.protocol
    )
    url = f'{address}/confirmation_blocks/{block_identifier}'

    try:
        results = fetch(url=url, headers={})
        return results
    except Exception as e:
        logger.exception(e)


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


def send_confirmation_block_history_request():
    """
    Request missing blocks from the primary validator
    """

    head_block_hash = cache.get(HEAD_BLOCK_HASH)
    self_configuration = get_self_configuration(exception_class=RuntimeError)
    primary_validator = self_configuration.primary_validator

    address = format_address(
        ip_address=primary_validator.ip_address,
        port=primary_validator.port,
        protocol=primary_validator.protocol
    )
    url = f'{address}/confirmation_block_history/{head_block_hash}'

    try:
        results = fetch(url=url, headers={})
        return results
    except Exception as e:
        logger.exception(e)


def set_primary_validator(*, validator):
    """
    Set validator as primary validator
    """

    self_configuration = get_self_configuration(exception_class=RuntimeError)
    self_configuration.primary_validator = validator
    self_configuration.save()

    connect_to_primary_validator(primary_validator=validator)
    sync_blockchains(primary_validator=validator)


def sync_blockchains(*, primary_validator):
    """
    Sync blockchains with the primary validator
    - clear CONFIRMATION_BLOCK_QUEUE
    - determine the starting block to sync from
    - send a request for any missing blocks

    Starting confirmation block order of operations:

    1. self HEAD_BLOCK_HASH - attempt to append blocks onto this nodes existing blockchain

    2. PV seed_block_identifier - if PV does not have block matching the self HEAD_BLOCK_HASH, sync from the
    PVs seed_block_identifier

    3. PV root_account_file_hash - if no PV seed_block_identifier exists, that indicates that the PV has began as a
    brand new network and we therefore must sync from the root_account_file_hash
    """

    cache.set(CONFIRMATION_BLOCK_QUEUE, {}, None)
    head_block_hash = cache.get(HEAD_BLOCK_HASH)

    if head_block_hash:
        confirmation_block = fetch_confirmation_block(
            primary_validator=primary_validator,
            block_identifier=HEAD_BLOCK_HASH
        )

        if confirmation_block:
            send_confirmation_block_history_request()
            return

    sync_from_primary_validators_initial_block(primary_validator=primary_validator)


def sync_from_primary_validators_initial_block(*, primary_validator):
    """
    Sync from the primary validators initial block (seed_block_identifier or root_account_file_hash)

    Invoked when self (confirmation validator):
    - is first being initialized
    - has a blockchain that is out of sync with the PV
    """

    try:
        download_root_account_file(
            url=primary_validator.root_account_file,
            destination_file_path=settings.LOCAL_ROOT_ACCOUNT_FILE_PATH
        )
        file_hash = get_file_hash(settings.LOCAL_ROOT_ACCOUNT_FILE_PATH)

        # TODO: root_account_file should not be a copy of PVs URL but rather a unique path
        # TODO: this way, every validator maintains their own copy
        self_configuration = get_self_configuration(exception_class=RuntimeError)
        self_configuration.root_account_file = primary_validator.root_account_file
        self_configuration.root_account_file_hash = file_hash
        self_configuration.seed_block_identifier = primary_validator.seed_block_identifier
        self_configuration.save()

        sync_accounts_table_to_root_account_file()
    except Exception as e:
        logger.exception(e)
        raise RuntimeError(e)

    initial_block_identifier = self_configuration.seed_block_identifier or self_configuration.root_account_file_hash
    rebuild_cache(head_block_hash=initial_block_identifier)
    send_confirmation_block_history_request()


def sync_with_primary_validator(*, ip_address, port, protocol, trust=None):
    """
    Sync with primary validator
    """

    config = fetch_config(
        ip_address=ip_address,
        port=port,
        protocol=protocol
    )
    config = {k: v for k, v in config.items() if k in standard_field_names(Validator)}

    if trust is None:
        trust = get_trust(config=config)

    remove_existing_validators(config=config)
    serializer = PrimaryValidatorSyncSerializer(data=config)

    if serializer.is_valid():
        validator = serializer.save()
        validator.trust = trust
        validator.save()
        set_primary_validator(validator=validator)
        return

    logger.exception(serializer.errors)
    raise RuntimeError(serializer.errors)
