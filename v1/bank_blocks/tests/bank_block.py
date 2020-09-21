from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK


def test_bank_block_post(client, primary_validator_configuration, signed_block):
    client.post_json(
        reverse('bank_blocks-list'),
        signed_block,
        expected=HTTP_200_OK,
    )
