from django.core.cache import cache
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK

from thenewboston_validator.cache_tools.cache_keys import BLOCK_QUEUE


def test_bank_block_post(client, primary_validator_configuration, signed_block, celery_worker):
    response = client.post_json(
        reverse('bank_blocks-list'),
        signed_block,
        expected=HTTP_200_OK,
    )

    assert response == signed_block['block']
    assert cache.get(BLOCK_QUEUE) == [signed_block['block']]
