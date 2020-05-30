BANK_BLOCK_QUEUE = 'BANK_BLOCK_QUEUE'
CONFIRMATION_BLOCK_QUEUE = 'CONFIRMATION_BLOCK_QUEUE'
HEAD_HASH = 'HEAD_HASH'


def get_account_balance_cache_key(*, account_number):
    """
    Return cache key used for storing an accounts balance
    """

    return f'ACCOUNT_BALANCE:{account_number}'


def get_account_balance_lock_cache_key(*, account_number):
    """
    Return cache key used for storing an accounts balance lock
    """

    return f'ACCOUNT_BALANCE_LOCK:{account_number}'
