from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.cache import cache
from thenewboston.blocks.signatures import verify_signature
from thenewboston.utils.tools import sort_and_encode

from v1.banks.models.bank import Bank
from v1.constants.cache_keys import BANK_BLOCK_QUEUE
from .confirmed_blocks import sign_and_send_confirmed_block

logger = get_task_logger(__name__)


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

        bank = Bank.objects.filter(network_identifier=network_identifier).first()

        if not bank:
            logger.error(f'Bank with network_identifier {network_identifier} does not exist')
            continue

        verify_signature(
            message=sort_and_encode(block),
            signature=signature,
            verify_key=network_identifier
        )

        # TODO: Send error message back to bank if the sender doesn't have enough points

        sign_and_send_confirmed_block.delay(
            block=block,
            ip_address=bank.ip_address,
            port=bank.port,
            protocol=bank.protocol,
            url_path='/confirmation_blocks'
        )

    cache.set(BANK_BLOCK_QUEUE, [], None)


@shared_task
def process_confirmation_block_queue():
    """
    Process confirmation block queue
    """

    pass
