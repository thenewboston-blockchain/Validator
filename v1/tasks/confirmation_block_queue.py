import logging
from decimal import Decimal

from celery import shared_task
from dateutil.relativedelta import relativedelta
from django.core.cache import cache
from django.utils import timezone

from v1.banks.models.bank import Bank
from v1.cache_tools.cache_keys import CONFIRMATION_BLOCK_QUEUE, HEAD_BLOCK_HASH
from v1.self_configurations.helpers.self_configuration import get_self_configuration
from .helpers import format_updated_balances, get_updated_accounts, is_block_valid

logger = logging.getLogger('thenewboston')


def handle_bank_confirmation_services(*, block, self_configuration):
    """
    Check validated block to see if there are any payments to self from banks
    If so, convert to confirmation service time
    """

    sender_account_number = block['account_number']
    message = block['message']
    txs = message['txs']

    self_account_number = self_configuration.account_number
    self_daily_confirmation_rate = self_configuration.daily_confirmation_rate

    confirmation_service_amount = next(
        (tx['amount'] for tx in txs if tx['recipient'] == self_account_number),
        None
    )

    if not confirmation_service_amount:
        return

    bank = Bank.objects.filter(account_number=sender_account_number).first()

    if not bank:
        return

    # TODO: Can probably split this up into another function

    current_confirmation_expiration = bank.confirmation_expiration
    now = timezone.now()

    if not current_confirmation_expiration:
        base_confirmation_expiration = now
    else:
        base_confirmation_expiration = max([current_confirmation_expiration, now])

    confirmation_service_amount = Decimal(str(confirmation_service_amount))
    days_purchased = confirmation_service_amount / self_daily_confirmation_rate
    seconds_purchased = days_purchased * 86400
    seconds_purchased = int(seconds_purchased)

    bank.confirmation_expiration = base_confirmation_expiration + relativedelta(seconds=seconds_purchased)
    bank.save()

    # TODO: Send POST /validator_confirmation_services to bank

    return seconds_purchased


@shared_task
def process_confirmation_block_queue():
    """
    Process confirmation block queue
    - this is for confirmation validators only
    """

    # TODO: Optimize
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

    updated_balances = format_updated_balances(existing_accounts, new_accounts)

    # TODO: Compare updated balances
    print(updated_balances)
    print(confirmation_block['updated_balances'])

    # TODO: Run as task
    handle_bank_confirmation_services(
        block=block,
        self_configuration=self_configuration
    )

    # TODO: Remove only this confirmation block from the CONFIRMATION_BLOCK_QUEUE, do not empty the entire queue
