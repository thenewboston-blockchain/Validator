import pytest
from django.core.cache import cache
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND

from thenewboston_validator.cache_tools.cache_keys import HEAD_BLOCK_HASH
from thenewboston_validator.cache_tools.queued_confirmation_blocks import add_queued_confirmation_block
from thenewboston_validator.cache_tools.valid_confirmation_blocks import add_valid_confirmation_block


@pytest.fixture(autouse=True)
def confirmation_primary_validator(confirmation_validator_configuration):
    pass


def test_confirmation_block_post(client, confirmation_block_data, celery_worker):

    key = confirmation_block_data['message']['block_identifier']
    cache.set(HEAD_BLOCK_HASH, key, None)

    client.post_json(
        reverse('confirmation_blocks-list'),
        confirmation_block_data,
        expected=HTTP_201_CREATED,
    )


def test_confirmation_block_queued_200(client, confirmation_block_data, block_identifier):
    add_queued_confirmation_block(confirmation_block=confirmation_block_data['message'])

    result = client.get_json(
        reverse(
            'confirmation_blocks-queued',
            args=[block_identifier],
        ),
        expected=HTTP_200_OK,
    )
    assert result == confirmation_block_data['message']


def test_confirmation_block_queued_404(client, confirmation_block_data, block_identifier):
    client.get_json(
        reverse(
            'confirmation_blocks-queued',
            args=[block_identifier],
        ),
        expected=HTTP_404_NOT_FOUND,
    )


def test_confirmation_block_valid_200(client, confirmation_block_data, block_identifier):
    add_valid_confirmation_block(confirmation_block=confirmation_block_data)

    result = client.get_json(
        reverse(
            'confirmation_blocks-valid',
            args=[block_identifier],
        ),
        expected=HTTP_200_OK,
    )
    assert result == confirmation_block_data


def test_confirmation_block_valid_404(client, block_identifier):
    client.get_json(
        reverse(
            'confirmation_blocks-valid',
            args=[block_identifier],
        ),
        expected=HTTP_404_NOT_FOUND,
    )
