from django.core.validators import MaxValueValidator
from django.db import models
from thenewboston.constants.network import PROTOCOL_CHOICES, VERIFY_KEY_LENGTH
from thenewboston.models.network_registration import NetworkRegistration

from v1.validators.models.validator import Validator

"""
The ValidatorRegistration model represents a connection between two validators. This can be between either:
CV <--> PV
CV <--> CV

The "source" is the validator that initiated the request and the "target" is the recipient.
"""


class ValidatorRegistration(NetworkRegistration):
    validator = models.ForeignKey(Validator, on_delete=models.CASCADE, blank=True, null=True)

    # Source validator
    source_ip_address = models.GenericIPAddressField()
    source_node_identifier = models.CharField(max_length=VERIFY_KEY_LENGTH)
    source_port = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[
            MaxValueValidator(65535)
        ]
    )
    source_protocol = models.CharField(choices=PROTOCOL_CHOICES, max_length=5)

    # Target validator
    target_ip_address = models.GenericIPAddressField()
    target_node_identifier = models.CharField(max_length=VERIFY_KEY_LENGTH)
    target_port = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[
            MaxValueValidator(65535)
        ]
    )
    target_protocol = models.CharField(choices=PROTOCOL_CHOICES, max_length=5)

    class Meta:
        default_related_name = 'validator_registrations'

    def __str__(self):
        return (
            f'ID: {self.id} | '
            f'Source NID: {self.source_node_identifier} | '
            f'Target NID: {self.target_node_identifier} | '
            f'Status: {self.status}'
        )
