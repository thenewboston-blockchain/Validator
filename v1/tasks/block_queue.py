import logging

from celery import shared_task
from django.core.cache import cache
from sentry_sdk import capture_exception
from thenewboston.utils.format import format_address
from thenewboston.utils.network import post

from v1.cache_tools.cache_keys import BLOCK_QUEUE, BLOCK_QUEUE_CACHE_LOCK_KEY
from v1.cache_tools.valid_confirmation_blocks import add_valid_confirmation_block
from v1.self_configurations.helpers.self_configuration import get_self_configuration
from v1.validators.models.validator import Validator
from .confirmation_blocks import sign_block_to_confirm_and_update_head_block_hash
from .helpers import get_updated_accounts, is_block_valid, update_accounts_cache, update_accounts_table

logger = logging.getLogger('thenewboston')


@shared_task
def process_block_queue():
    """
    Process block queue
    - this is for primary validators only
    """

    with cache.lock(BLOCK_QUEUE_CACHE_LOCK_KEY):
        block_queue = cache.get(BLOCK_QUEUE)

        if block_queue:
            cache.set(BLOCK_QUEUE, [], None)

    for block in block_queue:
        is_valid, sender_account_balance = is_block_valid(block=block)

        if not is_valid:
            continue

        existing_accounts, new_accounts = get_updated_accounts(
            sender_account_balance=sender_account_balance,
            validated_block=block
        )
        update_accounts_cache(
            existing_accounts=existing_accounts,
            new_accounts=new_accounts
        )
        update_accounts_table(
            existing_accounts=existing_accounts,
            new_accounts=new_accounts
        )
        confirmation_block, head_block_hash = sign_block_to_confirm_and_update_head_block_hash(
            block=block,
            existing_accounts=existing_accounts,
            new_accounts=new_accounts
        )
        add_valid_confirmation_block(confirmation_block=confirmation_block)
        send_confirmation_block_to_confirmation_validators.delay(confirmation_block=confirmation_block)


@shared_task
def send_confirmation_block_to_confirmation_validators(*, confirmation_block):
    """
    Send confirmed block to confirmation validators
    This function is called by the primary validator only
    - confirmation validators send their confirmation blocks to their banks
    """

    # TODO: Optimize
    self_configuration = get_self_configuration(exception_class=RuntimeError)
    confirmation_validators = Validator.objects.exclude(node_identifier=self_configuration.node_identifier)

    for validator in confirmation_validators:
        address = format_address(
            ip_address=validator.ip_address,
            port=validator.port,
            protocol=validator.protocol
        )
        url = f'{address}/confirmation_blocks'

        try:
            post(url=url, body=confirmation_block)
        except Exception as e:
            capture_exception(e)
            logger.exception(e)
