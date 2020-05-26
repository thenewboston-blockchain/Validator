from hashlib import sha3_256 as sha3

from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.cache import cache
from thenewboston.blocks.signatures import verify_signature
from thenewboston.utils.tools import sort_and_encode

from v1.constants.cache_keys import BANK_BLOCK_QUEUE, BLOCK_CHAIN_HEAD_HASH, block_cache_key

logger = get_task_logger(__name__)


def get_block_hash_value(*, block):
    """
    Generate a balance lock from a Tx
    """

    return sha3(sort_and_encode(block)).digest().hex()


@shared_task
def process_bank_block_queue():
    """
    Process bank block queue
    """

    bank_block_queue = cache.get(BANK_BLOCK_QUEUE)
    block_chain_head_hash = cache.get(BLOCK_CHAIN_HEAD_HASH)

    for bank_block in bank_block_queue:
        block = bank_block.get('block')
        message = sort_and_encode(block)
        verify_signature(
            account_number=bank_block.get('confirmation_identifier'),
            signature=bank_block.get('signature'),
            message=message
        )
        confirmed_block = {
            **block,
            'block_identifier': block_chain_head_hash
        }
        block_hash_value = get_block_hash_value(block=confirmed_block)
        cache.set(BLOCK_CHAIN_HEAD_HASH, block_hash_value, None)
        cache.set(block_cache_key(block_hash_value), confirmed_block, None)

        # TODO: Send this out to the original bank and all backup validators
        logger.warning(confirmed_block)

    cache.set(BANK_BLOCK_QUEUE, [], None)
