import pytest
from thenewboston.utils.format import format_address
from v1.banks.serializers.bank import BankSerializer
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from thenewboston.utils.signed_requests import generate_signed_request
from v1.banks.models.bank import Bank


@pytest.mark.parametrize(
    'code, message',
    [(HTTP_201_CREATED, ''), (HTTP_400_BAD_REQUEST, 'Already connected to bank')]
)
def test_validator_post_bank(client, bank, requests_mock, signing_key, code, message):
    if code == HTTP_201_CREATED:
        Bank.objects.all().delete()

    bank_address = format_address(
        ip_address=bank.ip_address,
        port=bank.port,
        protocol=bank.protocol
    )
    bank_config_response = BankSerializer(bank).data
    bank_config_response['node_type'] = 'BANK'
    bank_config_response['primary_validator'] = {}
    requests_mock.get(
        f'{bank_address}/config',
        json=bank_config_response,
    )
    print(f'aaaaa {BankSerializer(bank).data}')

    response = client.post_json(
        reverse('connection_requests'),
        generate_signed_request(
            data={
                "ip_address": bank.ip_address,
                "port": bank.port,
                "protocol": bank.protocol,
            },
            nid_signing_key=signing_key
        ),
        expected=code
    )

    if message:
        assert message in response
