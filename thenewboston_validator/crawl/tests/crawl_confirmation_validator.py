import pytest
from django.core.cache import cache
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from thenewboston.constants.crawl import (
    CRAWL_COMMAND_START,
    CRAWL_COMMAND_STOP,
    CRAWL_STATUS_CRAWLING,
    CRAWL_STATUS_NOT_CRAWLING,
    CRAWL_STATUS_STOP_REQUESTED
)
from thenewboston.utils.signed_requests import generate_signed_request

from thenewboston_validator.cache_tools.cache_keys import CRAWL_LAST_COMPLETED, CRAWL_STATUS
from thenewboston_validator.self_configurations.helpers.signing_key import get_signing_key
from ..helpers import get_crawl_info
from ..serializers.crawl import CrawlSerializer


@pytest.fixture(autouse=True)
def self_configuration(confirmation_validator_configuration):
    return confirmation_validator_configuration


def crawl_request(client, command, status):
    return client.post_json(
        reverse('crawl-list'),
        generate_signed_request(
            data={
                'crawl': command
            },
            nid_signing_key=get_signing_key()
        ),
        expected=status,
    )


def crawl_status(client):
    return client.get_json(
        reverse('crawl-list'),
        expected=HTTP_200_OK,
    )


def test_crawl_start_200(client, settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    crawl_request(client, CRAWL_COMMAND_START, HTTP_200_OK)

    assert cache.get(CRAWL_LAST_COMPLETED) is not None
    assert cache.get(CRAWL_STATUS) == CRAWL_STATUS_NOT_CRAWLING

    status = crawl_status(client)
    assert status['crawl_last_completed'] is not None
    assert status['crawl_status'] == CRAWL_STATUS_NOT_CRAWLING


def test_crawl_start_400_already_crawling(client):
    cache.set(CRAWL_STATUS, CRAWL_STATUS_CRAWLING, None)

    response = crawl_request(client, CRAWL_COMMAND_START, HTTP_400_BAD_REQUEST)
    assert response['crawl'] == [CrawlSerializer().error_messages['cant_start_crawl']]
    assert crawl_status(client)['crawl_status'] == CRAWL_STATUS_CRAWLING


def test_crawl_start_400_stop_requested(client):
    cache.set(CRAWL_STATUS, CRAWL_STATUS_STOP_REQUESTED, None)

    response = crawl_request(client, CRAWL_COMMAND_START, HTTP_400_BAD_REQUEST)
    assert response['crawl'] == [CrawlSerializer().error_messages['cant_start_crawl']]
    assert crawl_status(client)['crawl_status'] == CRAWL_STATUS_STOP_REQUESTED


def test_crawl_stop_200(client, settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True

    cache.set(CRAWL_STATUS, CRAWL_STATUS_CRAWLING, None)
    response = crawl_request(client, CRAWL_COMMAND_STOP, HTTP_200_OK)

    assert response['crawl_status'] == CRAWL_STATUS_STOP_REQUESTED
    assert cache.get(CRAWL_STATUS) == CRAWL_STATUS_STOP_REQUESTED


def test_crawl_stop_400_not_crawling(client):
    cache.set(CRAWL_STATUS, CRAWL_STATUS_NOT_CRAWLING, None)
    response = crawl_request(client, CRAWL_COMMAND_STOP, HTTP_400_BAD_REQUEST)

    assert response['crawl'] == [CrawlSerializer().error_messages['cant_stop_crawl']]
    assert crawl_status(client)['crawl_status'] == CRAWL_STATUS_NOT_CRAWLING


@pytest.mark.parametrize(
    'status',
    [
        CRAWL_STATUS_CRAWLING,
        CRAWL_STATUS_NOT_CRAWLING,
        CRAWL_STATUS_STOP_REQUESTED
    ]
)
def test_crawl_status_200(client, status):
    cache.set(CRAWL_STATUS, status, None)
    result = crawl_status(client)

    assert result['crawl_status'] == status
    assert result == get_crawl_info()
