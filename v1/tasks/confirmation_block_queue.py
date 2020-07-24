import json

from celery import shared_task
from django.core.cache import cache

from v1.cache_tools.cache_keys import CONFIRMATION_BLOCK_QUEUE, HEAD_BLOCK_HASH
from v1.self_configurations.helpers.self_configuration import get_self_configuration
from .bank_confirmation_services import handle_bank_confirmation_services
from .helpers import format_updated_balances, get_updated_accounts, is_block_valid


@shared_task
def process_confirmation_block_queue():
    """
    Process confirmation block queue
    - this is for confirmation validators only
    """

    self_configuration = get_self_configuration(exception_class=RuntimeError)
    confirmation_block_queue = cache.get(CONFIRMATION_BLOCK_QUEUE)
    head_block_hash = cache.get(HEAD_BLOCK_HASH)

    confirmation_block = next((i for i in confirmation_block_queue if i['block_identifier'] == head_block_hash), None)

    if not confirmation_block:
        return

    block = confirmation_block['block']
    is_valid, sender_account_balance = is_block_valid(block=block)

    if not is_valid:
        # TODO: Switch primary validators (to self of next trusted)
        print('The primary validator is cheating')
        return

    existing_accounts, new_accounts = get_updated_accounts(
        sender_account_balance=sender_account_balance,
        validated_block=block
    )

    if not updated_balances_match(
        confirmation_block['updated_balances'],
        format_updated_balances(existing_accounts, new_accounts)
    ):
        # TODO: Switch primary validators (to self of next trusted)
        print('The primary validator is cheating')
        return

    # TODO: Run as task
    handle_bank_confirmation_services(
        block=block,
        self_account_number=self_configuration.account_number
    )

    # TODO: Remove only this confirmation block from the CONFIRMATION_BLOCK_QUEUE, do not empty the entire queue


def updated_balances_match(a, b):
    """
    Compare two lists of dicts to determine if they are identical
    """

    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
