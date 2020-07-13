from decimal import Decimal

from dateutil.relativedelta import relativedelta
from django.utils import timezone

from v1.banks.models.bank import Bank


def handle_bank_confirmation_services(*, block, self_configuration):
    """
    Check validated block to see if there are any payments to self from banks
    If so, convert to confirmation service time
    """

    sender_account_number = block['account_number']
    message = block['message']
    txs = message['txs']

    self_account_number = self_configuration.account_number
    self_daily_confirmation_rate = self_configuration.daily_confirmation_rate

    confirmation_service_amount = next(
        (tx['amount'] for tx in txs if tx['recipient'] == self_account_number),
        None
    )

    if not confirmation_service_amount:
        return

    bank = Bank.objects.filter(account_number=sender_account_number).first()

    if not bank:
        return

    # TODO: Can probably split this up into another function

    current_confirmation_expiration = bank.confirmation_expiration
    now = timezone.now()

    if not current_confirmation_expiration:
        base_confirmation_expiration = now
    else:
        base_confirmation_expiration = max([current_confirmation_expiration, now])

    confirmation_service_amount = Decimal(str(confirmation_service_amount))
    days_purchased = confirmation_service_amount / self_daily_confirmation_rate
    seconds_purchased = days_purchased * 86400
    seconds_purchased = int(seconds_purchased)

    bank.confirmation_expiration = base_confirmation_expiration + relativedelta(seconds=seconds_purchased)
    bank.save()

    # TODO: Send POST /validator_confirmation_services to bank

    return seconds_purchased
