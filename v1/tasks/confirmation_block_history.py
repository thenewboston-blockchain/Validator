import logging

from celery import shared_task
from django.core.cache import cache
from thenewboston.utils.format import format_address
from thenewboston.utils.messages import get_message_hash
from thenewboston.utils.network import post

from v1.cache_tools.cache_keys import get_confirmation_block_cache_key

logger = logging.getLogger('thenewboston')


@shared_task
def send_confirmation_block_history(*, block_identifier, ip_address, port, protocol):
    """
    Send historical confirmation blocks (starting with the block_identifier) to the confirmation validator
    """

    address = format_address(
        ip_address=ip_address,
        port=port,
        protocol=protocol
    )
    url = f'{address}/confirmation_blocks'

    confirmation_block_cache_key = get_confirmation_block_cache_key(block_identifier=block_identifier)
    confirmation_block = cache.get(confirmation_block_cache_key)

    while confirmation_block:

        try:
            post(url=url, body=confirmation_block)
        except Exception as e:
            logger.exception(e)

        block_identifier = get_message_hash(message=confirmation_block['message'])
        confirmation_block_cache_key = get_confirmation_block_cache_key(block_identifier=block_identifier)
        confirmation_block = cache.get(confirmation_block_cache_key)
