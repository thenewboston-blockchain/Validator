BLOCK_QUEUE = 'block-queue'
CONFIRMATION_BLOCK_QUEUE = 'confirmation-block-queue'
HEAD_BLOCK_HASH = 'head-block-hash'


def get_account_balance_cache_key(*, account_number):
    """
    Return cache key used for storing an accounts balance
    """

    return f'account:{account_number}:balance'


def get_account_balance_lock_cache_key(*, account_number):
    """
    Return cache key used for storing an accounts balance lock
    """

    return f'account:{account_number}:balance_lock'
