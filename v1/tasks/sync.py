import logging
from json import JSONDecodeError

from celery import shared_task
from django.core.cache import cache
from nacl.exceptions import BadSignatureError
from thenewboston.blocks.signatures import verify_signature
from thenewboston.utils.format import format_address
from thenewboston.utils.messages import get_message_hash
from thenewboston.utils.network import fetch
from thenewboston.utils.tools import sort_and_encode

from v1.cache_tools.cache_keys import HEAD_BLOCK_HASH
from v1.confirmation_blocks.serializers.confirmation_block import ConfirmationBlockSerializerCreate
from .confirmation_block_queue import process_confirmation_block_queue

logger = logging.getLogger('thenewboston')

"""
Functions used by confirmation validators when syncing with a primary validator

Logic handles:
- initial sync (when the confirmation validator first comes online)
- syncing to new primary validator (when directed by most trusted bank)
"""


def get_confirmation_block(*, address, block_identifier):
    """
    Return confirmation block chain segment
    """

    url = f'{address}/confirmation_blocks/{block_identifier}'
    results = fetch(url=url, headers={})
    return results


def get_confirmation_block_chain_segment(*, address, block_identifier):
    """
    Return confirmation block chain segment
    """

    url = f'{address}/confirmation_block_chain_segment/{block_identifier}'

    try:
        results = fetch(url=url, headers={})
        return results
    except JSONDecodeError:
        return []
    except Exception as e:
        print(e)
        return []


def get_confirmation_block_from_results(*, block_identifier, results):
    """
    Return the confirmation block from results list
    """

    return next((i for i in results if i['message']['block_identifier'] == block_identifier), None)


def populate_confirmation_block_queue(*, address, error_handler, initial_block_identifier):
    """
    Fetch confirmation blocks from primary validator starting with initial_block_identifier
    Add all confirmation blocks to confirmation block queue
    """

    block_identifier = initial_block_identifier
    results = get_confirmation_block_chain_segment(address=address, block_identifier=block_identifier)

    error = False

    while results and not error:
        confirmation_block = get_confirmation_block_from_results(
            block_identifier=block_identifier,
            results=results
        )

        while confirmation_block:
            message = confirmation_block['message']

            try:
                verify_signature(
                    message=sort_and_encode(message),
                    signature=confirmation_block['signature'],
                    verify_key=confirmation_block['node_identifier']
                )
            except BadSignatureError as e:
                error_handler(e)
                error = True
                break
            except Exception as e:
                error_handler(e)
                error = True
                break

            serializer = ConfirmationBlockSerializerCreate(data=message)

            if serializer.is_valid():
                _bid = serializer.save()
                print(_bid)
            else:
                error_handler(serializer.errors)
                error = True
                break

            block_identifier = get_message_hash(message=message)
            confirmation_block = get_confirmation_block_from_results(
                block_identifier=block_identifier,
                results=results
            )

        if error:
            break

        results = get_confirmation_block_chain_segment(address=address, block_identifier=block_identifier)


@shared_task
def sync_to_new_primary_validator(*, ip_address, port, protocol):
    """
    Sync to new primary validator (as directed by most trusted bank)
    """

    address = format_address(
        ip_address=ip_address,
        port=port,
        protocol=protocol
    )
    populate_confirmation_block_queue(
        address=address,
        error_handler=logger.exception,
        initial_block_identifier=cache.get(HEAD_BLOCK_HASH)
    )
    process_confirmation_block_queue()
