from django.utils import timezone

from v1.banks.models.bank import Bank


def get_banks_with_active_confirmation_services():
    """
    Return queryset of banks with active confirmation services
    """

    return Bank.objects.filter(confirmation_expiration__gte=timezone.now()).distinct()
