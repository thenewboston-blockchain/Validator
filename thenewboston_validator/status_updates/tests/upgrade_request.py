import pytest
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from thenewboston.constants.network import CONFIRMATION_VALIDATOR, PRIMARY_VALIDATOR
from thenewboston.utils.signed_requests import generate_signed_request

from thenewboston_validator.banks.helpers.most_trusted import get_most_trusted_bank


@pytest.mark.parametrize(
    'self_configuration, node, node_type_before, node_type_after, status',
    [
        (
            'confirmation_validator_configuration',
            'confirmation_validator_configuration',
            CONFIRMATION_VALIDATOR,
            PRIMARY_VALIDATOR,
            HTTP_200_OK,
        ),
        (
            'confirmation_validator_configuration',
            'bank',
            CONFIRMATION_VALIDATOR,
            CONFIRMATION_VALIDATOR,
            HTTP_400_BAD_REQUEST,
        ),
        (
            'primary_validator_configuration',
            'primary_validator_configuration',
            PRIMARY_VALIDATOR,
            PRIMARY_VALIDATOR,
            HTTP_200_OK,
        )
    ]
)
def test_upgrade_request(
    request, self_configuration, node, node_type_before, node_type_after, status,
    client, bank, signing_key, celery_worker
):
    self_configuration = request.getfixturevalue(self_configuration)
    node = request.getfixturevalue(node)

    bank.trust = get_most_trusted_bank().trust + 1
    bank.save()

    client.post_json(
        reverse('upgrade_request-list'),
        generate_signed_request(
            data={
                'validator_node_identifier': node.node_identifier
            },
            nid_signing_key=signing_key
        ),
        expected=status
    )

    self_configuration.refresh_from_db()
    assert self_configuration.node_type == node_type_after
