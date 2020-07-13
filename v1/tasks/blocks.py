import logging

from celery import shared_task
from django.core.cache import cache
from nacl.encoding import HexEncoder
from nacl.signing import SigningKey
from thenewboston.environment.environment_variables import get_environment_variable
from thenewboston.utils.format import format_address
from thenewboston.utils.messages import get_message_hash
from thenewboston.utils.network import post
from thenewboston.utils.signed_requests import generate_signed_request

from v1.cache_tools.cache_keys import BLOCK_QUEUE, HEAD_BLOCK_HASH, get_confirmation_block_cache_key
from v1.self_configurations.helpers.self_configuration import get_self_configuration
from v1.validators.models.validator import Validator
from .helpers import (
    format_updated_balances,
    get_updated_accounts,
    is_block_valid,
    update_accounts_cache,
    update_accounts_table
)

logger = logging.getLogger('thenewboston')


@shared_task
def process_block_queue():
    """
    Process block queue
    """

    block_queue = cache.get(BLOCK_QUEUE)

    for block in block_queue:
        is_valid, sender_account_balance = is_block_valid(block=block)

        if not is_valid:
            continue

        existing_accounts, new_accounts = get_updated_accounts(
            sender_account_balance=sender_account_balance,
            validated_block=block
        )
        update_accounts_cache(
            existing_accounts=existing_accounts,
            new_accounts=new_accounts
        )
        update_accounts_table(
            existing_accounts=existing_accounts,
            new_accounts=new_accounts
        )
        confirmation_block = sign_block_to_confirm(
            block=block,
            existing_accounts=existing_accounts,
            new_accounts=new_accounts
        )
        send_confirmation_block_to_confirmation_validators(confirmation_block=confirmation_block)

    cache.set(BLOCK_QUEUE, [], None)


def send_confirmation_block_to_confirmation_validators(*, confirmation_block):
    """
    Send confirmed block to confirmation validators
    This function is called by the primary validator only
    - confirmation validators send their confirmation blocks to their banks
    """

    # TODO: Optimize
    self_configuration = get_self_configuration(exception_class=RuntimeError)
    confirmation_validators = Validator.objects.exclude(node_identifier=self_configuration.node_identifier)

    for validator in confirmation_validators:
        address = format_address(
            ip_address=validator.ip_address,
            port=validator.port,
            protocol=validator.protocol
        )
        url = f'{address}/confirmation_blocks'

        try:
            post(url=url, body=confirmation_block)
        except Exception as e:
            logger.exception(e)


def sign_block_to_confirm(*, block, existing_accounts, new_accounts):
    """
    Sign block to confirm validity
    Update HEAD_BLOCK_HASH
    """

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
