BANK_BLOCK_QUEUE = 'BANK_BLOCK_QUEUE'
BLOCK_CHAIN_HEAD_HASH = 'BLOCK_CHAIN_HEAD_HASH'
CONFIRMATION_BLOCK_QUEUE = 'CONFIRMATION_BLOCK_QUEUE'


def block_cache_key(block_hash):
    """
    Return cache key for (confirmed) blocks
    """

    return f'BLOCK_{block_hash}'
