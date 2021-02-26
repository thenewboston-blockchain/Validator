from django.core.cache import cache
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_404_NOT_FOUND
from thenewboston.constants.clean import CLEAN_COMMAND_START
from thenewboston.utils.signed_requests import generate_signed_request

from thenewboston_validator.cache_tools.cache_keys import CLEAN_STATUS
from thenewboston_validator.self_configurations.helpers.signing_key import get_signing_key


def test_clean_start_200(client, primary_validator_configuration):
    client.post_json(
        reverse('clean-list'),
        generate_signed_request(
            data={
                'clean': CLEAN_COMMAND_START
            },
            nid_signing_key=get_signing_key(),
        ),
        expected=HTTP_404_NOT_FOUND,
    )
    assert cache.get(CLEAN_STATUS) is None


def test_clean_status_200(client, primary_validator_configuration):
    client.get_json(
        reverse('clean-list'),
        expected=HTTP_404_NOT_FOUND,
    )
