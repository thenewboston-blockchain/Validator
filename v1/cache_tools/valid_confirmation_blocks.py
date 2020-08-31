from django.core.cache import cache

from .constants import VALID_CONFIRMATION_BLOCK


def add_valid_confirmation_block(*, confirmation_block):
    """
    Add valid confirmation block to the cache
    """

    key = get_valid_confirmation_block_cache_key(
        block_identifier=confirmation_block['block_identifier']
    )
    cache.set(key, confirmation_block, None)


def delete_all_valid_confirmation_blocks():
    """
    Delete all valid confirmation blocks from the cache
    """

    cache.delete_pattern(f'{VALID_CONFIRMATION_BLOCK}:*')


def get_all_valid_confirmation_blocks():
    """
    Return a set of all valid confirmation blocks
    """

    keys = cache.keys(f'{VALID_CONFIRMATION_BLOCK}:*')
    return cache.get_many(keys)


def get_valid_confirmation_block_cache_key(*, block_identifier):
    """
    Return cache key used for storing valid confirmation blocks
    """

    return f'{VALID_CONFIRMATION_BLOCK}:{block_identifier}'
