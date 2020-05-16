from django.core.exceptions import ValidationError
from django.db import models

from v1.constants.models import NODE_TYPE_CHOICES
from v1.network.constants.nodes import VALIDATOR
from v1.network.models.network_node import NetworkNode

"""
primary - when set to True, validator will accept incoming bank transactions as the primary validator
"""


class SelfConfiguration(NetworkNode):
    node_type = models.CharField(choices=NODE_TYPE_CHOICES, default=VALIDATOR, max_length=9)
    primary = models.BooleanField(default=False)

    class Meta:
        default_related_name = 'self_configurations'

    def __str__(self):
        return (
            f'Node type: {self.node_type} | '
            f'Primary: {self.primary} | '
            f'Version: {self.version}'
        )

    def _validate(self, error):
        """
        Ensure only one SelfConfiguration exists
        """

        if not self.id and SelfConfiguration.objects.exists():
            raise error('Only one SelfConfiguration allowed')

    def clean(self):
        self._validate(ValidationError)

    def save(self, *args, **kwargs):
        self._validate(RuntimeError)
        super().save(*args, **kwargs)
