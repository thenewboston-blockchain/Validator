from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.cache import cache
from thenewboston.blocks.signatures import verify_signature
from thenewboston.utils.tools import sort_and_encode

from v1.constants.cache_keys import BANK_BLOCK_QUEUE

logger = get_task_logger(__name__)


@shared_task
def process_bank_block_queue():
    """
    Process bank block queue
    """

    bank_block_queue = cache.get(BANK_BLOCK_QUEUE)

    for bank_block in bank_block_queue:
        block = bank_block.get('block')
        message = sort_and_encode(block)
        verify_signature(
            account_number=bank_block.get('confirmation_identifier'),
            signature=bank_block.get('signature'),
            message=message
        )
        logger.info(block)
