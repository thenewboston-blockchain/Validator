from celery import shared_task
from celery.utils.log import get_task_logger
from thenewboston.utils.format import format_address
from thenewboston.utils.network import fetch

from v1.registrations.models.bank_registration import BankRegistration

logger = get_task_logger(__name__)


@shared_task
def process_bank_registration(*, bank_registration_id, txs):
    """
    Process bank registration
    """

    bank_registration = BankRegistration.objects.get(id=bank_registration_id)

    # TODO: Update balance sheet
    print(txs)

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
    # TODO: Just send the serialized BankRegistration object with the updated status
    print(results)
