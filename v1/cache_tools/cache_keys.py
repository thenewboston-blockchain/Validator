BLOCK_QUEUE = 'block-queue'
HEAD_BLOCK_HASH = 'head-block-hash'

# Cache key prefixes
QUEUED_CONFIRMATION_BLOCK = 'queued-confirmation-block'
VALID_CONFIRMATION_BLOCK = 'valid-confirmation-block'


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


def get_queued_confirmation_block_cache_key(*, block_identifier):
    """
    Return cache key used for storing queued confirmation blocks
    """

    return f'{QUEUED_CONFIRMATION_BLOCK}:{block_identifier}'


def get_valid_confirmation_block_cache_key(*, block_identifier):
    """
    Return cache key used for storing valid confirmation blocks
    """

    return f'{VALID_CONFIRMATION_BLOCK}:{block_identifier}'
