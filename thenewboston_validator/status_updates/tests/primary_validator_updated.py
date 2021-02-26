from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from thenewboston.utils.signed_requests import generate_signed_request

from thenewboston_validator.banks.helpers.most_trusted import get_most_trusted_bank


def primary_validator_updated(client, signing_key, validator, status):
    return client.post_json(
        reverse('primary_validator_updated-list'),
        generate_signed_request(
            data={
                'ip_address': validator.ip_address,
                'port': validator.port,
                'protocol': validator.protocol,
            },
            nid_signing_key=signing_key
        ),
        expected=status
    )


def test_primary_validator_updated_200_not_changed(client, signing_key, bank, confirmation_validator_configuration):
    primary_validator = confirmation_validator_configuration.primary_validator
    primary_validator_updated(client, signing_key, primary_validator, HTTP_200_OK)

    confirmation_validator_configuration.refresh_from_db()
    assert confirmation_validator_configuration.primary_validator == primary_validator


def test_primary_validator_updated_200_not_available(
    client, signing_key, bank, confirmation_validator_configuration, validator
):
    primary_validator = validator
    primary_validator.ip_address = '127.0.0.1'

    bank.trust = get_most_trusted_bank().trust + 1
    bank.save()

    result = primary_validator_updated(client, signing_key, primary_validator, HTTP_400_BAD_REQUEST)
    assert result == ['Networks out of sync']


def test_primary_validator_updated_400_low_trust(
    client,
    signing_key,
    bank,
    confirmation_validator_configuration,
    validator
):
    primary_validator = validator

    bank.trust = get_most_trusted_bank().trust - 1
    bank.save()

    result = primary_validator_updated(client, signing_key, primary_validator, HTTP_400_BAD_REQUEST)
    assert result == ['Networks out of sync']
