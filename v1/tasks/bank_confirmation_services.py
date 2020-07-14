from decimal import Decimal

from dateutil.relativedelta import relativedelta
from django.utils import timezone

from v1.banks.models.bank import Bank
from v1.self_configurations.helpers.self_configuration import get_self_configuration
from .signed_requests import send_signed_post_request


def create_confirmation_service(*, bank, confirmation_service_amount):
    """
    Create confirmation service for bank
    """

    current_confirmation_expiration = bank.confirmation_expiration
    now = timezone.now()

    if not current_confirmation_expiration:
        start = now
    else:
        start = max([current_confirmation_expiration, now])

    self_configuration = get_self_configuration(exception_class=RuntimeError)
    daily_confirmation_rate = self_configuration.daily_confirmation_rate

    confirmation_service_amount = Decimal(str(confirmation_service_amount))
    days_purchased = confirmation_service_amount / daily_confirmation_rate
    seconds_purchased = days_purchased * 86400
    seconds_purchased = int(seconds_purchased)

    end = start + relativedelta(seconds=seconds_purchased)
    bank.confirmation_expiration = end
    bank.save()

    send_signed_post_request.delay(
        data={
            'end': str(end),
            'start': str(start)
        },
        ip_address=bank.ip_address,
        port=bank.port,
        protocol=bank.protocol,
        url_path='/validator_confirmation_services'
    )

    return seconds_purchased


def handle_bank_confirmation_services(*, block, self_account_number):
    """
    Check validated block to see if there are any payments to self from banks
    If so, convert to confirmation service time
    """

    message = block['message']
    txs = message['txs']

    confirmation_service_amount = next(
        (tx['amount'] for tx in txs if tx['recipient'] == self_account_number),
        None
    )

    if not confirmation_service_amount:
        return

    bank = Bank.objects.filter(account_number=block['account_number']).first()

    if not bank:
        return

    seconds_purchased = create_confirmation_service(
        bank=bank,
        confirmation_service_amount=confirmation_service_amount
    )

    return seconds_purchased
