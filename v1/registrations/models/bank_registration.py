from django.db import models

from v1.banks.models.bank import Bank
from v1.network.models.network_registration import NetworkRegistration


class BankRegistration(NetworkRegistration):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, blank=True, null=True)
    identifier = models.CharField(max_length=256)
    ip_address = models.GenericIPAddressField()

    class Meta:
        default_related_name = 'bank_registrations'

    def __str__(self):
        return (
            f'ID: {self.id} | '
            f'Identifier: {self.identifier} | '
            f'IP address: {self.ip_address} | '
            f'Status: {self.status}'
        )
