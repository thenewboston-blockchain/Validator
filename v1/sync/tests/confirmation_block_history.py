from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK

from v1.cache_tools.valid_confirmation_blocks import add_valid_confirmation_block


def test_confirmation_block_history_post(client, confirmation_block_data, signed_confirmation_block_history_request):
    add_valid_confirmation_block(confirmation_block=confirmation_block_data)
    response = client.post_json(
        reverse('confirmation_block_history-list'),
        signed_confirmation_block_history_request,
        expected=HTTP_200_OK,
    )
    assert response == signed_confirmation_block_history_request
