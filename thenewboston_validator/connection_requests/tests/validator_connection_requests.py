from rest_framework.reverse import reverse
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from thenewboston_validator.validators.models.validator import Validator


def test_connection_requests_post_validator_success(
    client, validator, validator_config, requests_mock, validator_connection_requests_signed_request, validator_address
):
    Validator.objects.all().delete()

    requests_mock.get(
        f'{validator_address}/config',
        json=validator_config,
    )

    response = client.post_json(
        reverse('connection_requests'),
        validator_connection_requests_signed_request,
        expected=HTTP_201_CREATED,
    )
    assert response == {}
    assert Validator.objects.filter(
        ip_address=validator.ip_address, protocol=validator.protocol, port=validator.port
    ).exists()


def test_connection_requests_post_primary_validator(
    client, validator, validator_config_primary_node, requests_mock,
    validator_connection_requests_signed_request, validator_address
):
    Validator.objects.all().delete()

    requests_mock.get(
        f'{validator_address}/config',
        json=validator_config_primary_node,
    )

    response = client.post_json(
        reverse('connection_requests'),
        validator_connection_requests_signed_request,
        expected=HTTP_400_BAD_REQUEST
    )

    assert 'Unable to accept connection requests from primary validators' in response['non_field_errors'][0]


def test_connection_requests_post_from_unknown_node(
    client, validator, config_unknown_node, requests_mock,
    validator_connection_requests_signed_request, validator_address
):
    Validator.objects.all().delete()

    requests_mock.get(
        f'{validator_address}/config',
        json=config_unknown_node,
    )

    response = client.post_json(
        reverse('connection_requests'),
        validator_connection_requests_signed_request,
        expected=HTTP_400_BAD_REQUEST
    )

    assert 'Invalid node_type' in response['non_field_errors'][0]


def test_connection_requests_post_validator_existed_validate_node_identifier(
    client, validator_connection_requests_signed_request
):
    response = client.post_json(
        reverse('connection_requests'),
        validator_connection_requests_signed_request,
        expected=HTTP_400_BAD_REQUEST,
    )

    assert response['node_identifier'] == ['Validator with that node identifier already exists']


def test_connection_requests_post_validator_already_connected(
    client, validator_connection_requests_signed_request_new_node_identifier,
):
    response = client.post_json(
        reverse('connection_requests'),
        validator_connection_requests_signed_request_new_node_identifier,
        expected=HTTP_400_BAD_REQUEST,
    )
    assert response['non_field_errors'] == ['Already connected to validator']


def test_connection_requests_post_connection_requests_to_itself(
    client, validator_connection_requests_signed_request_connect_to_itself
):
    response = client.post_json(
        reverse('connection_requests'),
        validator_connection_requests_signed_request_connect_to_itself,
        expected=HTTP_400_BAD_REQUEST,
    )
    assert response['non_field_errors'] == ['Unable to connect to self']
