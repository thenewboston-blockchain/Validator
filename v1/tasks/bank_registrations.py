from celery import shared_task
from celery.utils.log import get_task_logger
from thenewboston.constants.network import ACCEPTED
from thenewboston.utils.format import format_address
from thenewboston.utils.network import fetch

from v1.bank_registrations.models.bank_registration import BankRegistration
from .signed_requests import send_signed_patch_request

logger = get_task_logger(__name__)


@shared_task
def process_bank_registration(*, bank_registration_pk, block, source_bank_registration_pk):
    """
    Process bank registration
    """

    bank_registration = BankRegistration.objects.get(id=bank_registration_pk)

    # TODO: Update balance sheet
    # TODO: Need to make sure only to approve their registration once their block is validated (async though)
    # TODO: Safe just to check balance, won't impact balance sheet in any way
    print(block)

    # TODO: Do background check on Bank, if good update status to ACCEPTED
    # TODO: If ACCEPTED create Bank if it doesn't exist
    # TODO: Set proper Bank FK on BankRegistration
    # TODO: Send a **signed** PATCH request to the bank letting them know of the results either way
    address = format_address(
        ip_address=bank_registration.ip_address,
        port=bank_registration.port,
        protocol=bank_registration.protocol
    )
    config_address = f'{address}/config'
    print(config_address)

    results = fetch(url=config_address, headers={})

    # TODO: Check that configs match, if so approve (if not decline)
    print(results)

    bank_registration.status = ACCEPTED
    bank_registration.save()

    send_signed_patch_request(
        data={
            'status': ACCEPTED
        }, 
        ip_address=bank_registration.ip_address,
        port=bank_registration.port,
        protocol=bank_registration.protocol,
        url_path=f'/bank_registrations/{source_bank_registration_pk}'
    )
