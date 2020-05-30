from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.cache import cache
from thenewboston.blocks.signatures import verify_signature
from thenewboston.utils.tools import sort_and_encode

from v1.banks.models.bank import Bank
from v1.constants.cache_keys import BANK_BLOCK_QUEUE, get_account_cache_key
from .confirmed_blocks import sign_and_send_confirmed_block

logger = get_task_logger(__name__)


def is_total_amount_valid(*, block, sender_account):
    """
    Validate total amount
    """

    txs = block['txs']
    total_amount = sum([tx['amount'] for tx in txs])
    sender_balance = sender_account['balance']

    if total_amount > sender_balance:
        error = f'Transaction total of {total_amount} is greater than account balance of {sender_balance}'
        return False, error

    return True, None


@shared_task
def process_bank_block_queue():
    """
    Process bank block queue
    """

    bank_block_queue = cache.get(BANK_BLOCK_QUEUE)

    for bank_block in bank_block_queue:
        block = bank_block.get('block')
        network_identifier = bank_block.get('network_identifier')
        signature = bank_block.get('signature')

        bank = Bank.objects.filter(network_identifier=network_identifier).first()

        if not bank:
            logger.error(f'Bank with network_identifier {network_identifier} does not exist')
            continue

        verify_signature(
            message=sort_and_encode(block),
            signature=signature,
            verify_key=network_identifier
        )

        sender_account_number = block['account_number']
        sender_account_cache_key = get_account_cache_key(account_number=sender_account_number)
        sender_account = cache.get(sender_account_cache_key)

        if not sender_account:
            logger.error(f'Account number {sender_account_number} does not exist')
            continue

        total_amount_valid, error = is_total_amount_valid(block=block, sender_account=sender_account)

        if not total_amount_valid:
            logger.error(error)
            continue

        sign_and_send_confirmed_block.delay(
            block=block,
            ip_address=bank.ip_address,
            port=bank.port,
            protocol=bank.protocol,
            url_path='/confirmation_blocks'
        )

    cache.set(BANK_BLOCK_QUEUE, [], None)


@shared_task
def process_confirmation_block_queue():
    """
    Process confirmation block queue
    """

    pass
