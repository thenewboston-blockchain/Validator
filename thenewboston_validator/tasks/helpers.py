import logging
from operator import itemgetter

from django.core.cache import cache
from nacl.exceptions import BadSignatureError
from sentry_sdk import capture_exception
from thenewboston.blocks.signatures import verify_signature
from thenewboston.utils.messages import get_message_hash
from thenewboston.utils.tools import sort_and_encode

from thenewboston_validator.accounts.models.account import Account
from thenewboston_validator.cache_tools.accounts import get_account_balance, get_account_balance_lock
from thenewboston_validator.cache_tools.cache_keys import get_account_balance_cache_key, get_account_balance_lock_cache_key

logger = logging.getLogger('thenewboston')


def format_updated_balances(existing_accounts, new_accounts):
    """
    Standardize shape of updated balances

    Convert balance to string to ensure it is JSON serializable
    """
    updated_balances = existing_accounts + new_accounts
    return sorted(updated_balances, key=itemgetter('account_number'))


def get_updated_accounts(*, sender_account_balance, validated_block):
    """Return the updated balances of all accounts involved"""
    existing_accounts = []
    new_accounts = []

    message = validated_block['message']
    txs = message['txs']
    total_amount = sum([tx['amount'] for tx in txs])

    existing_accounts.append({
        'account_number': validated_block['account_number'],
        'balance': sender_account_balance - total_amount,
        'balance_lock': get_message_hash(message=message)
    })

    for tx in txs:
        amount = tx['amount']
        recipient = tx['recipient']
        recipient_account_balance = get_account_balance(account_number=recipient)

        if recipient_account_balance is None:
            new_accounts.append({
                'account_number': recipient,
                'balance': amount
            })
        else:
            existing_accounts.append({
                'account_number': recipient,
                'balance': recipient_account_balance + amount
            })

    return existing_accounts, new_accounts


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
        capture_exception(e)
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

    total_amount = sum([tx['amount'] for tx in txs])

    if total_amount > account_balance:
        error = f'Transaction total of {total_amount} is greater than account balance of {account_balance}'
        return False, error

    return True, None


def update_accounts_cache(*, existing_accounts, new_accounts):
    """Update accounts cache"""
    for account in existing_accounts:
        account_number = account['account_number']
        balance = account['balance']
        balance_lock = account.get('balance_lock')

        account_balance_cache_key = get_account_balance_cache_key(account_number=account_number)
        cache.set(account_balance_cache_key, balance, None)

        if balance_lock:
            account_balance_lock_cache_key = get_account_balance_lock_cache_key(account_number=account_number)
            cache.set(account_balance_lock_cache_key, balance_lock, None)

    for account in new_accounts:
        account_number = account['account_number']
        balance = account['balance']
        balance_lock = account_number

        account_balance_cache_key = get_account_balance_cache_key(account_number=account_number)
        account_balance_lock_cache_key = get_account_balance_lock_cache_key(account_number=account_number)
        cache.set(account_balance_cache_key, balance, None)
        cache.set(account_balance_lock_cache_key, balance_lock, None)


def update_accounts_table(*, existing_accounts, new_accounts):
    """Update or create accounts in the accounts table"""
    for account in existing_accounts:
        Account.objects.filter(
            account_number=account['account_number']
        ).update(
            **{k: v for k, v in account.items() if k != 'account_number'}
        )

    for account in new_accounts:
        account_number = account['account_number']

        Account.objects.create(
            account_number=account_number,
            balance=account['balance'],
            balance_lock=account_number
        )
