import random

from django.core.cache import cache
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED

from v1.cache_tools.cache_keys import BLOCK_QUEUE


def test_bank_block_post(client, primary_validator_configuration, signed_block, celery_worker):
    response = client.post_json(
        reverse('bank_blocks-list'),
        signed_block,
        expected=HTTP_200_OK,
    )

    assert response == signed_block['block']
    assert cache.get(BLOCK_QUEUE) == [signed_block['block']]


def test_validator_bank_block_max_length(client, primary_validator_configuration, signed_block, celery_worker):
    signed_block['block']['account_number'] = ''.join(random.choice('0123456789ABCDEF') for i in range(66))
    response = client.post_json(
        reverse('bank_blocks-list'),
        signed_block,
        expected=HTTP_401_UNAUTHORIZED,
    )

    assert response
