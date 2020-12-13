import pytest
from faker import Faker
from thenewboston.utils.format import format_address
from v1.banks.serializers.bank import BankSerializer
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from thenewboston.utils.signed_requests import generate_signed_request
from v1.banks.models.bank import Bank
from thenewboston.serializers.primary_validator import PrimaryValidatorSerializer
from thenewboston.constants.network import VERIFY_KEY_LENGTH
from thenewboston.verify_keys.verify_key import encode_verify_key


def test_connection_requests_post_bank_success(
    client, bank_config, requests_mock, bank_connection_requests_signed_request, bank_address
):
    Bank.objects.all().delete()

    requests_mock.get(
        f'{bank_address}/config',
        json=bank_config,
    )

    response = client.post_json(
        reverse('connection_requests'),
        bank_connection_requests_signed_request,
        expected=HTTP_201_CREATED,
    )
    assert response == {}


def test_connection_requests_post_bank_existed_validate_node_identifier(
    client, bank_connection_requests_signed_request
):
    response = client.post_json(
        reverse('connection_requests'),
        bank_connection_requests_signed_request,
        expected=HTTP_400_BAD_REQUEST,
    )

    assert response['node_identifier'] == ['Bank with that node identifier already exists']


def test_connection_requests_post_bank_already_connected(
    client, bank_connection_requests_signed_request_new_node_identifier,
):
    response = client.post_json(
        reverse('connection_requests'),
        bank_connection_requests_signed_request_new_node_identifier,
        expected=HTTP_400_BAD_REQUEST,
    )
    assert response['non_field_errors'] == ["Already connected to bank"]



