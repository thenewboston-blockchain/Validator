from rest_framework.reverse import reverse
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from thenewboston_validator.banks.models.bank import Bank


def test_connection_requests_post_bank_success(
    client, bank, bank_config, requests_mock, bank_connection_requests_signed_request, bank_address
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
    assert Bank.objects.filter(
        ip_address=bank.ip_address, protocol=bank.protocol, port=bank.port
    ).exists()


def test_connection_requests_post_from_bank_no_primary_config(
    client, bank, bank_config_no_primary_validator_info, requests_mock,
    bank_connection_requests_signed_request, bank_address
):
    Bank.objects.all().delete()

    requests_mock.get(
        f'{bank_address}/config',
        json=bank_config_no_primary_validator_info,
    )

    response = client.post_json(
        reverse('connection_requests'),
        bank_connection_requests_signed_request,
        expected=HTTP_400_BAD_REQUEST
    )
    assert response == {'primary_validator': ['This field is required.']}


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
    assert response['non_field_errors'] == ['Already connected to bank']
