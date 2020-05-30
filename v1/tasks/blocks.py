from celery import shared_task
from django.core.cache import cache
from thenewboston.blocks.signatures import verify_signature
from thenewboston.utils.tools import sort_and_encode

from v1.constants.cache_keys import BANK_BLOCK_QUEUE
from .confirmed_blocks import sign_and_send_confirmed_block


@shared_task
def process_bank_block_queue():
    """
    Process bank block queue
    """

    bank_block_queue = cache.get(BANK_BLOCK_QUEUE)

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

        sign_and_send_confirmed_block.delay(
            block=block,
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
