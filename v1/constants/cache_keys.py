BANK_BLOCK_QUEUE = 'BANK_BLOCK_QUEUE'
CONFIRMATION_BLOCK_QUEUE = 'CONFIRMATION_BLOCK_QUEUE'
HEAD_HASH = 'HEAD_HASH'


def get_account_cache_key(*, account_number):
    """
    Return cache key used for storing account information
    """

    return f'ACCOUNT:{account_number}'
