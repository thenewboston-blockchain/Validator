from django.core.validators import MaxValueValidator
from django.db import models

from v1.banks.models.bank import Bank
from thenewboston.constants.models import PROTOCOL_CHOICES
from thenewboston.models.network_registration import NetworkRegistration
from thenewboston.utils.format import format_node_address


class BankRegistration(NetworkRegistration):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, blank=True, null=True)
    identifier = models.CharField(max_length=256)
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
            f'Identifier: {self.identifier} | '
            f'IP address: {format_node_address(node=self)} | '
            f'Status: {self.status}'
        )
