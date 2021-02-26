import json
import logging

from celery import shared_task
from django.core.cache import cache
from sentry_sdk import capture_exception
from thenewboston.utils.format import format_address
from thenewboston.utils.network import post
from thenewboston.utils.signed_requests import generate_signed_request

from thenewboston_validator.banks.helpers.confirmation_services import get_banks_with_active_confirmation_services
from thenewboston_validator.cache_tools.cache_keys import HEAD_BLOCK_HASH
from thenewboston_validator.cache_tools.queued_confirmation_blocks import delete_queued_confirmation_block, get_queued_confirmation_block
from thenewboston_validator.cache_tools.valid_confirmation_blocks import add_valid_confirmation_block
from thenewboston_validator.self_configurations.helpers.self_configuration import get_self_configuration
from thenewboston_validator.self_configurations.helpers.signing_key import get_signing_key
from .bank_confirmation_services import handle_bank_confirmation_services
from .confirmation_blocks import sign_block_to_confirm_and_update_head_block_hash
from .helpers import (
    format_updated_balances,
    get_updated_accounts,
    is_block_valid,
    update_accounts_cache,
    update_accounts_table
)

logger = logging.getLogger('thenewboston')


@shared_task
def process_confirmation_block_queue():
    """
    Process confirmation block queue

    - this is for confirmation validators only

    Ran after:
    - initial sync with primary validator
    - receiving confirmation block from the primary validator
    """
    self_configuration = get_self_configuration(exception_class=RuntimeError)
    head_block_hash = cache.get(HEAD_BLOCK_HASH)
    confirmation_block = get_queued_confirmation_block(block_identifier=head_block_hash)

    while confirmation_block:
        block = confirmation_block['block']
        is_valid, sender_account_balance = is_block_valid(block=block)

        if not is_valid:
            send_invalid_block_to_banks(confirmation_block=confirmation_block)
            return

        existing_accounts, new_accounts = get_updated_accounts(
            sender_account_balance=sender_account_balance,
            validated_block=block
        )

        if not updated_balances_match(
            confirmation_block['updated_balances'],
            format_updated_balances(existing_accounts, new_accounts)
        ):
            send_invalid_block_to_banks(confirmation_block=confirmation_block)
            return

        update_accounts_cache(
            existing_accounts=existing_accounts,
            new_accounts=new_accounts
        )
        update_accounts_table(
            existing_accounts=existing_accounts,
            new_accounts=new_accounts
        )
        confirmation_block, head_block_hash = sign_block_to_confirm_and_update_head_block_hash(
            block=block,
            existing_accounts=existing_accounts,
            new_accounts=new_accounts
        )

        delete_queued_confirmation_block(block_identifier=confirmation_block['message']['block_identifier'])
        add_valid_confirmation_block(confirmation_block=confirmation_block)

        if self_configuration.daily_confirmation_rate:
            handle_bank_confirmation_services.delay(
                block=block,
                self_account_number=self_configuration.account_number
            )

        send_confirmation_block_to_banks(confirmation_block=confirmation_block)
        confirmation_block = get_queued_confirmation_block(block_identifier=head_block_hash)


def send_confirmation_block_to_banks(*, confirmation_block):
    """
    Send confirmed block to banks with active confirmation services

    This function is called by the confirmation validators only
    - primary validators send their confirmation blocks to the confirmation validators
    """
    for bank in get_banks_with_active_confirmation_services():
        address = format_address(
            ip_address=bank.ip_address,
            port=bank.port,
            protocol=bank.protocol
        )
        url = f'{address}/confirmation_blocks'

        try:
            post(url=url, body=confirmation_block)
        except Exception as e:
            capture_exception(e)
            logger.exception(e)


def send_invalid_block_to_banks(*, confirmation_block):
    """
    Send invalid block to banks

    This function is called by the confirmation validators only
    """
    block = confirmation_block['block']
    block_identifier = confirmation_block['block_identifier']

    self_configuration = get_self_configuration(exception_class=RuntimeError)
    primary_validator_node_identifier = self_configuration.primary_validator.node_identifier
    self_configuration.primary_validator = None
    self_configuration.save()

    invalid_block = generate_signed_request(
        data={
            'block': block,
            'block_identifier': block_identifier,
            'primary_validator_node_identifier': primary_validator_node_identifier
        },
        nid_signing_key=get_signing_key()
    )

    for bank in get_banks_with_active_confirmation_services():
        address = format_address(
            ip_address=bank.ip_address,
            port=bank.port,
            protocol=bank.protocol
        )
        url = f'{address}/invalid_blocks'

        try:
            post(url=url, body=invalid_block)
        except Exception as e:
            capture_exception(e)
            logger.exception(e)


def updated_balances_match(a, b):
    """Compare two lists of dicts to determine if they are identical"""
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
