import logging

from celery import shared_task
from django.core.cache import cache
from thenewboston.constants.network import ACCEPTED, DECLINED
from thenewboston.utils.fields import standard_field_names
from thenewboston.utils.format import format_address
from thenewboston.utils.network import fetch

from v1.bank_registrations.models.bank_registration import BankRegistration
from v1.banks.models.bank import Bank
from v1.banks.serializers.bank_configuration import BankConfigurationSerializer
from v1.cache_tools.cache_keys import (
    get_pending_bank_registration_pk_cache_key,
    get_pending_validator_registration_pk_cache_key
)
from .signed_requests import send_signed_patch_request

logger = logging.getLogger('thenewboston')


@shared_task
def handle_pending_registrations(*, block):
    """
    Check block recipients to see if self was included
    If so, check if there are pending bank or validator registrations that need processed
    Registrations will then be accepted after a background check
    """

    block_signature = block['signature']

    bank_registration_cache_key = get_pending_bank_registration_pk_cache_key(block_signature=block_signature)
    bank_registration_pk = cache.get(bank_registration_cache_key)

    if bank_registration_pk:
        process_bank_registration(bank_registration_pk=bank_registration_pk)
        return

    validator_registration_cache_key = get_pending_validator_registration_pk_cache_key(block_signature=block_signature)
    validator_registration_pk = cache.get(validator_registration_cache_key)

    if validator_registration_pk:
        print('Accept validator registration')
        return


def process_bank_registration(*, bank_registration_pk):
    """
    Process bank registration
    This function is ran after a banks registration block has been confirmed (paid)
    """

    bank_registration = BankRegistration.objects.get(id=bank_registration_pk)

    try:
        address = format_address(
            ip_address=bank_registration.ip_address,
            port=bank_registration.port,
            protocol=bank_registration.protocol
        )
        config_address = f'{address}/config'
        results = fetch(url=config_address, headers={})
    except Exception as e:
        logger.exception(e)
        bank_registration.status = DECLINED
        bank_registration.save()
        return

    serializer = BankConfigurationSerializer(data=results)

    if serializer.is_valid():
        excluded = ['trust']

        bank, _ = Bank.objects.update_or_create(
            ip_address=bank_registration.ip_address,
            defaults={
                k: v for k, v in results.items() if k in standard_field_names(Bank) and k not in excluded
            }
        )

        Bank.objects.filter(
            ip_address=bank_registration.ip_address
        ).exclude(
            node_identifier=bank_registration.node_identifier
        ).delete()

        bank_registration.bank = bank
        bank_registration.status = ACCEPTED
        bank_registration.save()
    else:
        logger.exception(serializer.errors)
        bank_registration.status = DECLINED
        bank_registration.save()

    send_signed_patch_request(
        data={
            'status': bank_registration.status
        },
        ip_address=bank_registration.ip_address,
        port=bank_registration.port,
        protocol=bank_registration.protocol,
        url_path=f'/bank_registrations/{bank_registration_pk}'
    )
