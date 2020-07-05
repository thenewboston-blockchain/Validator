from django.core.validators import MaxValueValidator
from django.db import models
from thenewboston.constants.network import PROTOCOL_CHOICES, VERIFY_KEY_LENGTH
from thenewboston.utils.format import format_node_address


class ConnectionRequest(models.Model):
    ip_address = models.GenericIPAddressField()
    node_identifier = models.CharField(max_length=VERIFY_KEY_LENGTH, unique=True)
    port = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[
            MaxValueValidator(65535)
        ]
    )
    protocol = models.CharField(choices=PROTOCOL_CHOICES, max_length=5)

    class Meta:
        default_related_name = 'connection_requests'
        constraints = [
            models.UniqueConstraint(
                fields=['ip_address', 'port'],
                name='unique_ip_address_port'
            )
        ]

    def __str__(self):
        return (
            f'ID: {self.id} | '
            f'Node Identifier: {self.node_identifier} | '
            f'Address: {format_node_address(node=self)}'
        )
