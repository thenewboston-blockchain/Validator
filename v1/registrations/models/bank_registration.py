from django.db import models

from v1.banks.models.bank import Bank
from v1.network.constants.models import PROTOCOL_CHOICES
from v1.network.models.network_registration import NetworkRegistration
from v1.network.utils.format import format_node_address


class BankRegistration(NetworkRegistration):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, blank=True, null=True)
    identifier = models.CharField(max_length=256)
    ip_address = models.GenericIPAddressField()
    port = models.PositiveSmallIntegerField(blank=True, null=True)
    protocol = models.CharField(choices=PROTOCOL_CHOICES, max_length=5)

    class Meta:
        default_related_name = 'bank_registrations'

    def __str__(self):
        return (
            f'ID: {self.id} | '
            f'Identifier: {self.identifier} | '
            f'IP address: {format_node_address(self)} | '
            f'Status: {self.status}'
        )
