from rest_framework.decorators import api_view
from rest_framework.response import Response
from thenewboston.utils.messages import get_message_hash

from thenewboston_validator.cache_tools.valid_confirmation_blocks import get_valid_confirmation_block
from ..helpers.block_identifier import get_initial_block_identifier


@api_view(['GET'])
def block_chain_view(_):
    """Return block chain"""
    block_chain = {}
    initial_block_identifier = get_initial_block_identifier()
    block_identifier = initial_block_identifier
    valid_confirmation_block = get_valid_confirmation_block(block_identifier=block_identifier)

    i = 0

    while valid_confirmation_block:
        block_chain[i] = valid_confirmation_block
        block_identifier = get_message_hash(message=valid_confirmation_block['message'])
        valid_confirmation_block = get_valid_confirmation_block(block_identifier=block_identifier)
        i += 1

    return Response({
        'initial_block_identifier': initial_block_identifier,
        'block_chain': block_chain
    })
