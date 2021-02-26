from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK
from thenewboston.constants.network import PRIMARY_VALIDATOR


def test_self_configuration_get(client, primary_validator_configuration):
    response = client.get_json(
        reverse('config-list'),
        expected=HTTP_200_OK,
    )
    primary_validator = response['primary_validator']
    node_type = response['node_type']

    assert primary_validator is None
    assert node_type == PRIMARY_VALIDATOR
