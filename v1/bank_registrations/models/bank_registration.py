from django.core.validators import MaxValueValidator
from django.db import models
from thenewboston.constants.network import PROTOCOL_CHOICES
from thenewboston.models.network_registration import NetworkRegistration
from thenewboston.utils.format import format_node_address

from v1.banks.models.bank import Bank


class BankRegistration(NetworkRegistration):
    account_number = models.CharField(max_length=256)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, blank=True, null=True)
    ip_address = models.GenericIPAddressField()
    port = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[
            MaxValueValidator(65535)
        ]
    )
    protocol = models.CharField(choices=PROTOCOL_CHOICES, max_length=5)

    class Meta:
        default_related_name = 'bank_registrations'

    def __str__(self):
        return (
            f'ID: {self.id} | '
            f'Account Number: {self.account_number} | '
            f'IP Address: {format_node_address(node=self)} | '
            f'Status: {self.status}'
        )
