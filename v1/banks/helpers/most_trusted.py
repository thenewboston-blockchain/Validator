from v1.banks.models.bank import Bank


def get_most_trusted_bank():
    """
    Return the validators most trusted bank
    """

    return Bank.objects.all().order_by('-trust').first()
