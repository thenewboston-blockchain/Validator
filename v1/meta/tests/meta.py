from django.core.cache import cache
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK

from v1.cache_tools.cache_keys import BLOCK_QUEUE
from v1.cache_tools.valid_confirmation_blocks import add_valid_confirmation_block


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

    print(response)
    assert response['block_queue'] == [block_data]
