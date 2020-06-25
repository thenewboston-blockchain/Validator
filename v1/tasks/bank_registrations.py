from celery import shared_task
from celery.utils.log import get_task_logger
from thenewboston.constants.network import ACCEPTED, DECLINED
from thenewboston.utils.fields import standard_field_names
from thenewboston.utils.format import format_address
from thenewboston.utils.network import fetch

from v1.bank_registrations.models.bank_registration import BankRegistration
from v1.banks.models.bank import Bank
from v1.banks.serializers.bank_configuration import BankConfigurationSerializer
from .signed_requests import send_signed_patch_request

logger = get_task_logger(__name__)


@shared_task
def process_bank_registration(*, block, pk):
    """
    Process bank registration
    """

    # TODO: Important!
    # TODO: This function needs to handle PVs and CVs (banks register with both)

    bank_registration = BankRegistration.objects.get(id=pk)

    # TODO: Update balance sheet
    # TODO: Need to make sure only to approve their registration once their block is validated (async though)
    # TODO: Safe just to check balance, won't impact balance sheet in any way
    print(block)

    # TODO: Do background check on Bank, if good update status to ACCEPTED
    address = format_address(
        ip_address=bank_registration.ip_address,
        port=bank_registration.port,
        protocol=bank_registration.protocol
    )
    config_address = f'{address}/config'
    results = fetch(url=config_address, headers={})
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
        # TODO: Proper error handling
        print(serializer.errors)
        bank_registration.status = DECLINED
        bank_registration.save()

    send_signed_patch_request(
        data={
            'status': bank_registration.status
        },
        ip_address=bank_registration.ip_address,
        port=bank_registration.port,
        protocol=bank_registration.protocol,
        url_path=f'/bank_registrations/{pk}'
    )
