from django.core.cache import cache

from thenewboston_validator.accounts.models.account import Account
from .cache_keys import get_account_balance_cache_key, get_account_balance_lock_cache_key


def get_account_balance(*, account_number):
    """Return balance for the given account_number"""
    account_balance_cache_key = get_account_balance_cache_key(account_number=account_number)
    account_balance = cache.get(account_balance_cache_key)

    if account_balance is None:
        account = Account.objects.filter(account_number=account_number).first()

        if account:
            return account.balance

    return account_balance


def get_account_balance_lock(*, account_number):
    """Return balance lock for the given account_number"""
    account_balance_lock_cache_key = get_account_balance_lock_cache_key(account_number=account_number)
    account_balance_lock = cache.get(account_balance_lock_cache_key)

    if account_balance_lock is None:
        account = Account.objects.filter(account_number=account_number).first()

        if account:
            return account.balance_lock

    return account_balance_lock
