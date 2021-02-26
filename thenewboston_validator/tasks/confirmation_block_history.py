import logging

from celery import shared_task
from sentry_sdk import capture_exception
from thenewboston.utils.format import format_address
from thenewboston.utils.messages import get_message_hash
from thenewboston.utils.network import post

from thenewboston_validator.cache_tools.valid_confirmation_blocks import get_valid_confirmation_block

logger = logging.getLogger('thenewboston')


@shared_task
def send_confirmation_block_history(*, block_identifier, ip_address, port, protocol):
    """Send historical confirmation blocks (starting with the block_identifier) to the confirmation validator"""
    address = format_address(
        ip_address=ip_address,
        port=port,
        protocol=protocol
    )
    url = f'{address}/confirmation_blocks'

    valid_confirmation_block = get_valid_confirmation_block(block_identifier=block_identifier)

    while valid_confirmation_block:

        try:
            post(url=url, body=valid_confirmation_block)
        except Exception as e:
            capture_exception(e)
            logger.exception(e)

        block_identifier = get_message_hash(message=valid_confirmation_block['message'])
        valid_confirmation_block = get_valid_confirmation_block(block_identifier=block_identifier)
