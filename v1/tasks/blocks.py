from decimal import Decimal
from hashlib import sha3_256 as sha3

from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.cache import cache
from nacl.encoding import HexEncoder
from nacl.exceptions import BadSignatureError
from nacl.signing import SigningKey
from thenewboston.blocks.balance_lock import generate_balance_lock
from thenewboston.blocks.signatures import verify_signature
from thenewboston.environment.environment_variables import get_environment_variable
from thenewboston.utils.signed_requests import generate_signed_request
from thenewboston.utils.tools import sort_and_encode

from v1.accounts.models.account import Account
from v1.cache_tools.accounts import get_account_balance, get_account_balance_lock
from v1.cache_tools.cache_keys import (
    BLOCK_QUEUE,
    HEAD_BLOCK_HASH,
    get_account_balance_cache_key,
    get_account_balance_lock_cache_key
)

logger = get_task_logger(__name__)


def get_message_hash(*, message):
    """
    Generate a balance lock from a Tx
    """

    return sha3(sort_and_encode(message)).digest().hex()


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
        is_valid, account_balance = is_block_valid(block=block)

        if not is_valid:
            continue

        process_validated_block(validated_block=block, sender_account_balance=account_balance)

    cache.set(BLOCK_QUEUE, [], None)


@shared_task
def process_confirmation_block_queue():
    """
    Process confirmation block queue
    - this is for backup validators only
    """

    pass


def process_validated_block(*, validated_block, sender_account_balance):
    """
    Update sender account
    Update recipient accounts
    Confirm (sign) block
    Send confirmed block to backup validators
    """

    sender_account_number = validated_block['account_number']
    sender_account_balance_cache_key = get_account_balance_cache_key(account_number=sender_account_number)
    sender_account_balance_lock_cache_key = get_account_balance_lock_cache_key(account_number=sender_account_number)

    message = validated_block['message']
    txs = message['txs']
    total_amount = sum([Decimal(str(tx['amount'])) for tx in txs])

    # Update sender account
    new_balance_lock = generate_balance_lock(message=validated_block['message'])
    cache.set(sender_account_balance_cache_key, Decimal(sender_account_balance) - total_amount)
    cache.set(sender_account_balance_lock_cache_key, new_balance_lock)

    # Update recipient accounts
    for tx in txs:
        amount = Decimal(str(tx['amount']))
        recipient = tx['recipient']
        recipient_account_balance_cache_key = get_account_balance_cache_key(account_number=recipient)
        recipient_account_balance = get_account_balance(account_number=recipient)

        if recipient_account_balance is None:
            cache.set(recipient_account_balance_cache_key, amount)
        else:
            cache.set(recipient_account_balance_cache_key, recipient_account_balance + amount)

    updated_balances = update_accounts_table(
        sender_account_number=sender_account_number,
        recipient_account_numbers=[tx['recipient'] for tx in txs]
    )

    confirmation_block = sign_block_to_confirm(block=validated_block, updated_balances=updated_balances)
    send_confirmation_block_to_backup_validators(confirmation_block=confirmation_block)


def send_confirmation_block_to_backup_validators(*, confirmation_block):
    """
    Send confirmed block to backup validators
    """

    # TODO: Send confirmed block to backup validators
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
    cache.set(HEAD_BLOCK_HASH, message_hash, None)

    return confirmation_block
