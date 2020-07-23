from v1.banks.models.bank import Bank


def is_most_trusted_bank(node_identifier) -> bool:
    bank = Bank.objects.all().order_by('-trust').first()

    return bank is not None and bank.node_identifier == node_identifier
