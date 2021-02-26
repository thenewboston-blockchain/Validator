from django.core.cache import cache
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK

from thenewboston_validator.cache_tools.cache_keys import BLOCK_QUEUE, HEAD_BLOCK_HASH, QUEUED_CONFIRMATION_BLOCK, VALID_CONFIRMATION_BLOCK
from thenewboston_validator.cache_tools.queued_confirmation_blocks import add_queued_confirmation_block
from thenewboston_validator.cache_tools.valid_confirmation_blocks import add_valid_confirmation_block


def test_block_chain_view(client, confirmation_validator_configuration, confirmation_block_data):
    add_valid_confirmation_block(confirmation_block=confirmation_block_data)

    response = client.get_json(
        reverse('meta/block_chain'),
        expected=HTTP_200_OK,
    )

    assert response['block_chain']['0'] == confirmation_block_data


def test_block_queue_view(client, block_data):
    cache.set(BLOCK_QUEUE, [block_data], None)
    response = client.get_json(
        reverse('meta/block_queue'),
        expected=HTTP_200_OK,
    )

    assert response['block_queue'] == [block_data]


def test_head_block_hash_view(client, block_identifier):
    cache.set(HEAD_BLOCK_HASH, block_identifier, None)
    response = client.get_json(
        reverse('meta/head_block_hash'),
        expected=HTTP_200_OK,
    )

    assert response['head_block_hash'] == block_identifier


def test_queued_confirmation_blocks_view(client, block_identifier, confirmation_block_data):
    add_queued_confirmation_block(confirmation_block=confirmation_block_data['message'])
    response = client.get_json(
        reverse('meta/queued_confirmation_blocks'),
        expected=HTTP_200_OK,
    )

    assert response['queued_confirmation_blocks'][
        f'{QUEUED_CONFIRMATION_BLOCK}:{block_identifier}'
    ] == confirmation_block_data['message']


def test_valid_confirmation_blocks_view(client, block_identifier, confirmation_block_data):
    add_valid_confirmation_block(confirmation_block=confirmation_block_data)
    response = client.get_json(
        reverse('meta/valid_confirmation_blocks'),
        expected=HTTP_200_OK,
    )

    assert response['valid_confirmation_blocks'][
        f'{VALID_CONFIRMATION_BLOCK}:{block_identifier}'
    ] == confirmation_block_data
