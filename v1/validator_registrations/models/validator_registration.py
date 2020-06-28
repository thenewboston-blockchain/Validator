from django.core.validators import MaxValueValidator
from django.db import models
from thenewboston.constants.network import PROTOCOL_CHOICES, VERIFY_KEY_LENGTH
from thenewboston.models.network_registration import NetworkRegistration
from thenewboston.utils.format import format_node_address

from v1.validators.models.validator import Validator


class ValidatorRegistration(NetworkRegistration):
    validator = models.ForeignKey(Validator, on_delete=models.CASCADE, blank=True, null=True)
    ip_address = models.GenericIPAddressField()
    node_identifier = models.CharField(max_length=VERIFY_KEY_LENGTH)
    port = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[
            MaxValueValidator(65535)
        ]
    )
    protocol = models.CharField(choices=PROTOCOL_CHOICES, max_length=5)

    class Meta:
        default_related_name = 'validator_registrations'

    def __str__(self):
        return (
            f'ID: {self.id} | '
            f'Node Identifier: {self.node_identifier} | '
            f'IP Address: {format_node_address(node=self)} | '
            f'Status: {self.status}'
        )
