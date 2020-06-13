from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.cache import cache
from thenewboston.blocks.balance_lock import generate_balance_lock
from thenewboston.blocks.signatures import verify_signature
from thenewboston.utils.tools import sort_and_encode

from v1.banks.models.bank import Bank
from v1.cache_tools.accounts import get_account_balance, get_account_balance_lock
from v1.cache_tools.cache_keys import BANK_BLOCK_QUEUE
from .confirmed_blocks import sign_and_send_validated_block

logger = get_task_logger(__name__)


def is_total_amount_valid(*, block, account_balance):
    """
    Validate total amount
    """

    message = block['message']
    txs = message['txs']

    total_amount = sum([tx['amount'] for tx in txs])

    if total_amount > account_balance:
        error = f'Transaction total of {total_amount} is greater than account balance of {account_balance}'
        return False, error

    return True, None


@shared_task
def process_bank_block_queue():
    """
    Process bank block queue

    For each bank block in the queue, verify:
    - banks signature
    - senders signature
    - account balance exists
    - amount sent does not exceed account balance
    - balance key matches balance lock
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

        # Verify banks signature
        verify_signature(
            message=sort_and_encode(block),
            signature=signature,
            verify_key=network_identifier
        )

        sender_account_number = block['account_number']
        sender_message = block['message']
        sender_signature = block['signature']
        sender_balance_key = sender_message['balance_key']

        # Verify senders signature
        verify_signature(
            message=sort_and_encode(sender_message),
            signature=sender_signature,
            verify_key=sender_account_number
        )

        sender_account_balance = get_account_balance(account_number=sender_account_number)
        sender_account_balance_lock = get_account_balance_lock(account_number=sender_account_number)

        # Verify account balance exists
        if sender_account_balance is None:
            logger.error(f'Account balance for {sender_account_number} not found')
            continue

        total_amount_valid, error = is_total_amount_valid(block=block, account_balance=sender_account_balance)

        # Verify amount sent does not exceed account balance
        if not total_amount_valid:
            logger.error(error)

        # Verify balance key matches balance lock
        if sender_balance_key != sender_account_balance_lock:
            logger.error(
                f'Balance key of {sender_balance_key} does not match balance lock of {sender_account_balance_lock}'
            )
            continue

        sign_and_send_validated_block.delay(
            block=block,
            ip_address=bank.ip_address,
            new_balance_lock=generate_balance_lock(message=block['message']),
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
