from decimal import Decimal

from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.cache import cache
from nacl.encoding import HexEncoder
from nacl.exceptions import BadSignatureError
from nacl.signing import SigningKey
from thenewboston.blocks.signatures import verify_signature
from thenewboston.environment.environment_variables import get_environment_variable
from thenewboston.utils.messages import get_message_hash
from thenewboston.utils.signed_requests import generate_signed_request
from thenewboston.utils.tools import sort_and_encode

from v1.accounts.models.account import Account
from v1.cache_tools.accounts import get_account_balance, get_account_balance_lock
from v1.cache_tools.cache_keys import (
    BLOCK_QUEUE,
    CONFIRMATION_BLOCK_QUEUE,
    HEAD_BLOCK_HASH,
    get_account_balance_cache_key,
    get_account_balance_lock_cache_key,
    get_confirmation_block_cache_key
)
from .registrations import handle_pending_registrations

logger = get_task_logger(__name__)


def is_block_valid(*, block):
    """
    For given block verify:
    - signature
    - account balance exists
    - amount sent does not exceed account balance
    - balance key matches balance lock

    Return boolean indicating validity, senders account balance
    """

    account_number = block.get('account_number')
    message = block.get('message')
    signature = block.get('signature')

    try:
        verify_signature(
            message=sort_and_encode(message),
            signature=signature,
            verify_key=account_number
        )
    except BadSignatureError:
        return False, None
    except Exception as e:
        logger.exception(e)
        return False, None

    account_balance = get_account_balance(account_number=account_number)
    account_balance_lock = get_account_balance_lock(account_number=account_number)

    if account_balance is None:
        logger.error(f'Account balance for {account_number} not found')
        return False, None

    total_amount_valid, error = is_total_amount_valid(block=block, account_balance=account_balance)

    if not total_amount_valid:
        logger.error(error)
        return False, None

    balance_key = message.get('balance_key')

    if balance_key != account_balance_lock:
        logger.error(
            f'Balance key of {balance_key} does not match balance lock of {account_balance_lock}'
        )
        return False, None

    return True, account_balance


def is_total_amount_valid(*, block, account_balance):
    """
    Validate total amount

    Return boolean indicating validity, error
    """

    message = block['message']
    txs = message['txs']

    total_amount = sum([Decimal(str(tx['amount'])) for tx in txs])

    if total_amount > account_balance:
        error = f'Transaction total of {total_amount} is greater than account balance of {account_balance}'
        return False, error

    return True, None


def update_accounts_table(*, sender_account_number, recipient_account_numbers):
    """
    Update the accounts table in the database
    Return updated balances
    """

    results = []

    sender_account_balance_cache_key = get_account_balance_cache_key(account_number=sender_account_number)
    sender_account_balance_lock_cache_key = get_account_balance_lock_cache_key(account_number=sender_account_number)
    sender_account_balance = cache.get(sender_account_balance_cache_key)
    sender_account_balance_lock = cache.get(sender_account_balance_lock_cache_key)

    Account.objects.filter(account_number=sender_account_number).update(
        balance=sender_account_balance,
        balance_lock=sender_account_balance_lock
    )

    results.append({
        'account_number': sender_account_number,
        'balance': str(sender_account_balance),
        'balance_lock': sender_account_balance_lock
    })

    for recipient in recipient_account_numbers:
        recipient_account_balance_cache_key = get_account_balance_cache_key(account_number=recipient)
        recipient_account_balance = cache.get(recipient_account_balance_cache_key)
        Account.objects.filter(account_number=recipient).update(balance=recipient_account_balance)

        results.append({
            'account_number': recipient,
            'balance': str(recipient_account_balance)
        })

    return results


@shared_task
def process_block_queue():
    """
    Process block queue
    """

    block_queue = cache.get(BLOCK_QUEUE)

    for block in block_queue:
        is_valid, sender_account_balance = is_block_valid(block=block)

        if not is_valid:
            continue

        handle_pending_registrations.delay(block=block)
        updated_balances = process_validated_block(
            validated_block=block,
            sender_account_balance=sender_account_balance
        )
        confirmation_block = sign_block_to_confirm(block=block, updated_balances=updated_balances)
        send_confirmation_block_to_backup_validators(confirmation_block=confirmation_block)

    cache.set(BLOCK_QUEUE, [], None)


@shared_task
def process_confirmation_block_queue():
    """
    Process confirmation block queue
    - this is for backup validators only
    """

    confirmation_block_queue = cache.get(CONFIRMATION_BLOCK_QUEUE)
    head_block_hash = cache.get(HEAD_BLOCK_HASH)

    confirmation_block = next((i for i in confirmation_block_queue if i['block_identifier'] == head_block_hash), None)

    logger.error(head_block_hash)
    logger.info(confirmation_block)

    if not confirmation_block:
        return

    block = confirmation_block['block']

    is_valid, sender_account_balance = is_block_valid(block=block)

    if not is_valid:
        # TODO: Change this
        print('This is not good')
        return

    updated_balances = process_validated_block(
        validated_block=block,
        sender_account_balance=sender_account_balance
    )

    # TODO: Compare updated balances
    print(updated_balances)
    print(confirmation_block['updated_balances'])

    # TODO: Remove only this confirmation block from the CONFIRMATION_BLOCK_QUEUE, do not empty the entire queue


def process_validated_block(*, validated_block, sender_account_balance):
    """
    Update sender account
    Update recipient accounts
    """

    sender_account_number = validated_block['account_number']
    sender_account_balance_cache_key = get_account_balance_cache_key(account_number=sender_account_number)
    sender_account_balance_lock_cache_key = get_account_balance_lock_cache_key(account_number=sender_account_number)

    message = validated_block['message']
    txs = message['txs']
    total_amount = sum([Decimal(str(tx['amount'])) for tx in txs])

    # Update sender account
    new_balance_lock = get_message_hash(message=validated_block['message'])
    cache.set(sender_account_balance_cache_key, Decimal(sender_account_balance) - total_amount, None)
    cache.set(sender_account_balance_lock_cache_key, new_balance_lock, None)

    # Update recipient accounts
    for tx in txs:
        amount = Decimal(str(tx['amount']))
        recipient = tx['recipient']
        recipient_account_balance_cache_key = get_account_balance_cache_key(account_number=recipient)
        recipient_account_balance = get_account_balance(account_number=recipient)

        if recipient_account_balance is None:
            cache.set(recipient_account_balance_cache_key, amount, None)
        else:
            cache.set(recipient_account_balance_cache_key, recipient_account_balance + amount, None)

    updated_balances = update_accounts_table(
        sender_account_number=sender_account_number,
        recipient_account_numbers=[tx['recipient'] for tx in txs]
    )

    return updated_balances


def send_confirmation_block_to_backup_validators(*, confirmation_block):
    """
    Send confirmed block to backup validators
    """

    # TODO: Send confirmed block to backup validators
    # TODO: This is for PV only

    print(confirmation_block)


def sign_block_to_confirm(*, block, updated_balances):
    """
    Sign block to confirm validity
    Update HEAD_BLOCK_HASH
    """

    head_block_hash = cache.get(HEAD_BLOCK_HASH)
    network_signing_key = get_environment_variable('NETWORK_SIGNING_KEY')
    signing_key = SigningKey(network_signing_key, encoder=HexEncoder)

    message = {
        'block': block,
        'block_identifier': head_block_hash,
        'updated_balances': updated_balances
    }
    confirmation_block = generate_signed_request(
        data=message,
        nid_signing_key=signing_key
    )

    message_hash = get_message_hash(message=message)
    confirmation_block_cache_key = get_confirmation_block_cache_key(block_identifier=head_block_hash)
    cache.set(confirmation_block_cache_key, confirmation_block, None)
    cache.set(HEAD_BLOCK_HASH, message_hash, None)

    # TODO: Remove these
    logger.error(confirmation_block_cache_key)
    logger.warning(confirmation_block)

    return confirmation_block
