import logging

from django.core.cache import cache
from sentry_sdk import capture_exception
from thenewboston.utils.messages import get_message_hash
from thenewboston.utils.signed_requests import generate_signed_request

from thenewboston_validator.cache_tools.cache_keys import HEAD_BLOCK_HASH
from thenewboston_validator.self_configurations.helpers.signing_key import get_signing_key
from .helpers import format_updated_balances

logger = logging.getLogger('thenewboston')


def sign_block_to_confirm_and_update_head_block_hash(*, block, existing_accounts, new_accounts):
    """
    Sign block to confirm validity

    Update HEAD_BLOCK_HASH
    """
    try:
        head_block_hash = cache.get(HEAD_BLOCK_HASH)

        message = {
            'block': block,
            'block_identifier': head_block_hash,
            'updated_balances': format_updated_balances(existing_accounts, new_accounts)
        }
        confirmation_block = generate_signed_request(
            data=message,
            nid_signing_key=get_signing_key()
        )

        message_hash = get_message_hash(message=message)
        cache.set(HEAD_BLOCK_HASH, message_hash, None)

        return confirmation_block, message_hash
    except Exception as e:
        capture_exception(e)
        logger.exception(e)
