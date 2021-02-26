from django.core.cache import cache
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_404_NOT_FOUND
from thenewboston.constants.crawl import CRAWL_COMMAND_START
from thenewboston.utils.signed_requests import generate_signed_request

from thenewboston_validator.cache_tools.cache_keys import CRAWL_STATUS
from thenewboston_validator.self_configurations.helpers.signing_key import get_signing_key


def test_crawl_start_200(client, primary_validator_configuration):
    client.post_json(
        reverse('crawl-list'),
        generate_signed_request(
            data={
                'crawl': CRAWL_COMMAND_START
            },
            nid_signing_key=get_signing_key(),
        ),
        expected=HTTP_404_NOT_FOUND,
    )
    assert cache.get(CRAWL_STATUS) is None


def test_crawl_status_200(client, primary_validator_configuration):
    client.get_json(
        reverse('crawl-list'),
        expected=HTTP_404_NOT_FOUND,
    )
