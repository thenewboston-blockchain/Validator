from django.core.cache import cache

from .cache_keys import QUEUED_CONFIRMATION_BLOCK, get_queued_confirmation_block_cache_key


def add_queued_confirmation_block(*, confirmation_block):
    """Add queued confirmation block to the cache"""
    key = get_queued_confirmation_block_cache_key(
        block_identifier=confirmation_block['block_identifier']
    )
    cache.set(key, confirmation_block, None)


def delete_all_queued_confirmation_blocks():
    """Delete all queued confirmation blocks from the cache"""
    cache.delete_pattern(f'{QUEUED_CONFIRMATION_BLOCK}:*')


def delete_queued_confirmation_block(*, block_identifier):
    """Delete queued confirmation blocks from the cache"""
    key = get_queued_confirmation_block_cache_key(block_identifier=block_identifier)
    cache.delete(key)


def get_all_queued_confirmation_blocks():
    """Return a set of all queued confirmation blocks"""
    keys = cache.keys(f'{QUEUED_CONFIRMATION_BLOCK}:*')
    return cache.get_many(keys)


def get_queued_confirmation_block(*, block_identifier):
    """Return queued confirmation block or None"""
    key = get_queued_confirmation_block_cache_key(block_identifier=block_identifier)
    return cache.get(key)
