from hashlib import sha3_256 as sha3

from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.cache import cache
from thenewboston.blocks.signatures import verify_signature
from thenewboston.utils.tools import sort_and_encode

from v1.constants.cache_keys import BANK_BLOCK_QUEUE, BLOCK_CHAIN_HEAD_HASH, block_cache_key
from .confirmed_blocks import sign_and_send_confirmed_block

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
        network_identifier = bank_block.get('network_identifier')
        signature = bank_block.get('signature')
        message = sort_and_encode(block)

        verify_signature(
            message=message,
            signature=signature,
            verify_key=network_identifier
        )

        # TODO: Send error message back to bank if the sender doesn't have enough points
        block_hash_value = get_block_hash_value(block=block)
        cache.set(block_cache_key(block_hash_value), block, None)
        cache.set(BLOCK_CHAIN_HEAD_HASH, block_hash_value, None)

        # TODO: Send this out to the original bank and all backup validators
        logger.warning(block)
        sign_and_send_confirmed_block.delay(
            block=block,
            block_identifier=block_chain_head_hash,
            ip_address='192.168.1.232',
            port=8000,
            protocol='http',
            url_path='/confirmation_blocks'
        )

    cache.set(BANK_BLOCK_QUEUE, [], None)


@shared_task
def process_confirmation_block_queue():
    """
    Process confirmation block queue
    """

    pass
