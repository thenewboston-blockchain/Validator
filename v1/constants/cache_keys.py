BANK_BLOCK_QUEUE = 'BANK_BLOCK_QUEUE'
BLOCK_CHAIN_HEAD_HASH = 'BLOCK_CHAIN_HEAD_HASH'


def block_cache_key(block_hash):
    """
    Return cache key for (confirmed) blocks
    """

    return f'BLOCK_{block_hash}'
