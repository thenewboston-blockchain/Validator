import logging

from django.core.cache import cache
from nacl.encoding import HexEncoder
from nacl.signing import SigningKey
from thenewboston.environment.environment_variables import get_environment_variable
from thenewboston.utils.messages import get_message_hash
from thenewboston.utils.signed_requests import generate_signed_request

from v1.cache_tools.cache_keys import HEAD_BLOCK_HASH, get_confirmation_block_cache_key
from .helpers import format_updated_balances

logger = logging.getLogger('thenewboston')


def sign_block_to_confirm(*, block, existing_accounts, new_accounts):
    """
    Sign block to confirm validity
    Update HEAD_BLOCK_HASH
    """

    try:
        head_block_hash = cache.get(HEAD_BLOCK_HASH)
        network_signing_key = get_environment_variable('NETWORK_SIGNING_KEY')
        signing_key = SigningKey(network_signing_key, encoder=HexEncoder)

        message = {
            'block': block,
            'block_identifier': head_block_hash,
            'updated_balances': format_updated_balances(existing_accounts, new_accounts)
        }
        confirmation_block = generate_signed_request(
            data=message,
            nid_signing_key=signing_key
        )

        message_hash = get_message_hash(message=message)
        confirmation_block_cache_key = get_confirmation_block_cache_key(block_identifier=head_block_hash)
        cache.set(confirmation_block_cache_key, confirmation_block, None)
        cache.set(HEAD_BLOCK_HASH, message_hash, None)

        return confirmation_block
    except Exception as e:
        logger.error(e)
        logger.exception(e)
