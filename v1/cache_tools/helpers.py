from django.core.cache import cache

from v1.accounts.models.account import Account
from .cache_keys import (
    BLOCK_QUEUE,
    CONFIRMATION_BLOCK_QUEUE,
    HEAD_BLOCK_HASH,
    get_account_balance_cache_key,
    get_account_balance_lock_cache_key
)


def rebuild_cache(*, head_block_hash):
    """
    Rebuild cache
    """

    cache.clear()
    cache.set(BLOCK_QUEUE, [], None)
    cache.set(CONFIRMATION_BLOCK_QUEUE, {}, None)
    cache.set(HEAD_BLOCK_HASH, head_block_hash, None)

    accounts = Account.objects.all()

    for account in accounts:
        account_number = account.account_number
        account_balance_cache_key = get_account_balance_cache_key(account_number=account_number)
        account_balance_lock_cache_key = get_account_balance_lock_cache_key(account_number=account_number)
        cache.set(account_balance_cache_key, account.balance, None)
        cache.set(account_balance_lock_cache_key, account.balance_lock, None)
