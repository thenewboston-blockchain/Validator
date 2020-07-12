import logging
from decimal import Decimal

from django.core.cache import cache
from nacl.exceptions import BadSignatureError
from thenewboston.blocks.signatures import verify_signature
from thenewboston.utils.messages import get_message_hash
from thenewboston.utils.tools import sort_and_encode

from v1.accounts.models.account import Account
from v1.cache_tools.accounts import get_account_balance, get_account_balance_lock
from v1.cache_tools.cache_keys import get_account_balance_cache_key, get_account_balance_lock_cache_key

logger = logging.getLogger('thenewboston')


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

        # TODO: Optimize
        if recipient_account_balance is None:
            cache.set(recipient_account_balance_cache_key, amount, None)
            Account.objects.create(
                account_number=recipient,
                balance=amount,
                balance_lock=recipient
            )
        else:
            cache.set(recipient_account_balance_cache_key, recipient_account_balance + amount, None)

    updated_balances = update_accounts_table(
        sender_account_number=sender_account_number,
        recipient_account_numbers=[tx['recipient'] for tx in txs]
    )

    return updated_balances


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
