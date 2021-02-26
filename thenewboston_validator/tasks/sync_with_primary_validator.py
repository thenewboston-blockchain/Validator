import logging

from celery import shared_task
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from sentry_sdk import capture_exception
from thenewboston.utils.fields import standard_field_names
from thenewboston.utils.files import get_file_hash
from thenewboston.utils.format import format_address
from thenewboston.utils.network import fetch, post
from thenewboston.utils.signed_requests import generate_signed_request

from thenewboston_validator.cache_tools.cache_keys import HEAD_BLOCK_HASH
from thenewboston_validator.cache_tools.helpers import rebuild_cache
from thenewboston_validator.cache_tools.queued_confirmation_blocks import delete_all_queued_confirmation_blocks
from thenewboston_validator.connection_requests.helpers.connect import connect_to_primary_validator
from thenewboston_validator.meta.helpers.block_identifier import get_initial_block_identifier
from thenewboston_validator.self_configurations.helpers.self_configuration import get_root_account_file_url, get_self_configuration
from thenewboston_validator.self_configurations.helpers.signing_key import get_signing_key
from thenewboston_validator.sync.helpers import download_root_account_file, sync_accounts_table_to_root_account_file
from thenewboston_validator.sync.serializers.primary_validator_sync import PrimaryValidatorSyncSerializer
from thenewboston_validator.validators.models.validator import Validator

logger = logging.getLogger('thenewboston')


def fetch_valid_confirmation_block(*, primary_validator, block_identifier):
    """Return valid confirmation block"""
    address = format_address(
        ip_address=primary_validator.ip_address,
        port=primary_validator.port,
        protocol=primary_validator.protocol
    )
    url = f'{address}/confirmation_blocks/{block_identifier}/valid'

    try:
        results = fetch(url=url, headers={})
        return results
    except Exception as e:
        capture_exception(e)
        logger.exception(e)


def get_trust(*, config):
    """Return trust level for existing validator"""
    validator = Validator.objects.filter(
        ip_address=config.get('ip_address'),
        node_identifier=config.get('node_identifier')
    ).first()

    if validator:
        return validator.trust

    return 0


def remove_existing_validators(*, config):
    """Remove any existing validators"""
    Validator.objects.filter(
        Q(ip_address=config.get('ip_address')) | Q(node_identifier=config.get('node_identifier'))
    ).delete()


def send_confirmation_block_history_request():
    """Request missing blocks from the primary validator"""
    self_configuration = get_self_configuration(exception_class=RuntimeError)
    primary_validator = self_configuration.primary_validator

    address = format_address(
        ip_address=primary_validator.ip_address,
        port=primary_validator.port,
        protocol=primary_validator.protocol
    )
    url = f'{address}/confirmation_block_history'

    signed_request = generate_signed_request(
        data={
            'block_identifier': cache.get(HEAD_BLOCK_HASH)
        },
        nid_signing_key=get_signing_key()
    )

    try:
        post(url=url, body=signed_request)
    except Exception as e:
        capture_exception(e)
        logger.exception(e)


def set_primary_validator(*, validator):
    """Set validator as primary validator"""
    self_configuration = get_self_configuration(exception_class=RuntimeError)
    self_configuration.primary_validator = validator
    self_configuration.save()

    connect_to_primary_validator(primary_validator=validator)
    sync_blockchains(primary_validator=validator)


def sync_blockchains(*, primary_validator):
    """
    Sync blockchains with the primary validator

    - delete all queued confirmation blocks
    - determine the starting block to sync from
    - send a request for any missing blocks

    Starting confirmation block order of operations:

    1. self HEAD_BLOCK_HASH - attempt to append blocks onto this nodes existing blockchain

    2. PV seed_block_identifier - if PV does not have block matching the self HEAD_BLOCK_HASH, sync from the
    PVs seed_block_identifier

    3. PV root_account_file_hash - if no PV seed_block_identifier exists, that indicates that the PV has began as a
    brand new network and we therefore must sync from the root_account_file_hash
    """
    delete_all_queued_confirmation_blocks()
    head_block_hash = cache.get(HEAD_BLOCK_HASH)

    if head_block_hash:
        valid_confirmation_block = fetch_valid_confirmation_block(
            primary_validator=primary_validator,
            block_identifier=head_block_hash
        )

        if valid_confirmation_block:
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
        self_configuration = get_self_configuration(exception_class=RuntimeError)
        download_root_account_file(url=primary_validator.root_account_file)

        self_configuration.root_account_file = get_root_account_file_url()
        self_configuration.root_account_file_hash = get_file_hash(settings.ROOT_ACCOUNT_FILE_PATH)
        self_configuration.seed_block_identifier = primary_validator.seed_block_identifier
        self_configuration.save()

        sync_accounts_table_to_root_account_file()
    except Exception as e:
        logger.exception(e)
        raise RuntimeError(e)

    rebuild_cache(head_block_hash=get_initial_block_identifier())
    send_confirmation_block_history_request()


@shared_task
def sync_with_primary_validator(*, config, trust=None):
    """Sync with primary validator"""
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
