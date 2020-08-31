BLOCK_QUEUE = 'block-queue'
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


def get_confirmation_block_cache_key(*, block_identifier):
    """
    Return cache key used for storing verified confirmation blocks
    """

    return f'confirmation_block:{block_identifier}'
