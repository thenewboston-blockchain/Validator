from django.core.exceptions import ValidationError
from django.db import models
from thenewboston.constants.network import VALIDATOR
from thenewboston.models.network_validator import NetworkValidator
from thenewboston.utils.fields import common_field_names

from v1.constants.models import NODE_TYPE_CHOICES
from v1.validators.models.validator import Validator

"""
primary - when set to True, validator will accept incoming bank transactions as the primary validator
"""


class SelfConfiguration(NetworkValidator):
    primary_validator = models.ForeignKey(Validator, on_delete=models.SET_NULL, blank=True, null=True)
    node_type = models.CharField(choices=NODE_TYPE_CHOICES, default=VALIDATOR, max_length=9)

    class Meta:
        default_related_name = 'self_configurations'

    def __str__(self):
        return (
            f'Node type: {self.node_type} | '
            f'Version: {self.version}'
        )

    def _update_related_validator(self):
        """
        Update related row in the validator table
        """

        validator = Validator.objects.filter(ip_address=self.ip_address)
        field_names = common_field_names(self, Validator)
        data = {f: getattr(self, f) for f in field_names}

        if validator:
            validator.update(**data)
        else:
            Validator.objects.create(**data, trust=100)

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
        self._update_related_validator()
