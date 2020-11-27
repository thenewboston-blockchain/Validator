from django.core.cache import cache

from .cache_keys import VALID_CONFIRMATION_BLOCK, get_valid_confirmation_block_cache_key


def add_valid_confirmation_block(*, confirmation_block):
    """Add valid confirmation block to the cache"""
    key = get_valid_confirmation_block_cache_key(
        block_identifier=confirmation_block['message']['block_identifier']
    )
    cache.set(key, confirmation_block, None)


def delete_all_valid_confirmation_blocks():
    """Delete all valid confirmation blocks from the cache"""
    cache.delete_pattern(f'{VALID_CONFIRMATION_BLOCK}:*')


def get_all_valid_confirmation_blocks():
    """Return a set of all valid confirmation blocks"""
    keys = cache.keys(f'{VALID_CONFIRMATION_BLOCK}:*')
    return cache.get_many(keys)


def get_valid_confirmation_block(*, block_identifier):
    """Return valid confirmation block or None"""
    key = get_valid_confirmation_block_cache_key(block_identifier=block_identifier)
    return cache.get(key)
