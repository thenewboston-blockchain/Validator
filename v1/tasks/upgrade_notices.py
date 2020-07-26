import logging

from celery import shared_task
from thenewboston.utils.format import format_address
from thenewboston.utils.network import post
from thenewboston.utils.signed_requests import generate_signed_request

from v1.banks.models.bank import Bank
from v1.self_configurations.helpers.signing_key import get_signing_key

logger = logging.getLogger('thenewboston')


@shared_task
def send_upgrade_notices(*, requesting_banks_node_identifier):
    """
    Description:
    - notice from a previous confirmation validator that they are now a primary validator
    - triggered from an /upgrade_request from the validators most trusted bank
    - banks that trust self more than their existing primary validator will set self as new primary validator
    - banks that do not trust self more than their existing primary validator will remain on their existing network and
      can therefore be deleted

    Responses:
    - 200 response > bank set self as new primary validator
    - 400 response > bank is remaining on their existing network (can be deleted)

    Notes:
        The requesting (most trusted) bank may be excluded from notice recipients since it will already receive the
        updated information from the /upgrade_request response
    """

    banks = Bank.objects.all().exclude(node_identifier=requesting_banks_node_identifier)

    for bank in banks:
        signed_request = generate_signed_request(
            data={
                'bank_node_identifier': bank.node_identifier
            },
            nid_signing_key=get_signing_key()
        )
        node_address = format_address(
            ip_address=bank.ip_address,
            port=bank.port,
            protocol=bank.protocol,
        )
        url = f'{node_address}/upgrade_notice'

        try:
            post(url=url, body=signed_request)
        except Exception as e:
            bank.delete()
            logger.exception(e)
