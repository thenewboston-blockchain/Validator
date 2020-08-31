from django.core.cache import cache

from .constants import QUEUED_CONFIRMATION_BLOCK


def add_queued_confirmation_block(*, confirmation_block):
    """
    Add queued confirmation block to the cache
    """

    cache_key = get_queued_confirmation_block_cache_key(
        block_identifier=confirmation_block['block_identifier']
    )
    cache.set(cache_key, confirmation_block, None)


def delete_all_queued_confirmation_blocks():
    """
    Delete all queued confirmation blocks from the cache
    """

    cache.delete_pattern(f'{QUEUED_CONFIRMATION_BLOCK}:*')


def get_all_queued_confirmation_blocks():
    """
    Return a set of all queued confirmation blocks
    """

    keys = cache.iter_keys(f'{QUEUED_CONFIRMATION_BLOCK}:*')
    return cache.get_many(keys)


def get_queued_confirmation_block_cache_key(*, block_identifier):
    """
    Return cache key used for storing queued confirmation blocks
    """

    return f'{QUEUED_CONFIRMATION_BLOCK}:{block_identifier}'
