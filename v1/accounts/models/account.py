from uuid import uuid4

from django.core.validators import MinValueValidator
from django.db import models
from thenewboston.constants.network import BALANCE_LOCK_LENGTH, VERIFY_KEY_LENGTH
from thenewboston.utils.validators import validate_is_real_number


class Account(models.Model):
    id = models.UUIDField(default=uuid4, editable=False, primary_key=True)
    account_number = models.CharField(max_length=VERIFY_KEY_LENGTH, unique=True)
    balance = models.DecimalField(
        decimal_places=16,
        default=0,
        max_digits=32,
        validators=[
            MinValueValidator(0),
            validate_is_real_number
        ]
    )
    balance_lock = models.CharField(max_length=BALANCE_LOCK_LENGTH, unique=True)

    class Meta:
        default_related_name = 'accounts'

    def __str__(self):
        return (
            f'Account Number: {self.account_number} | '
            f'Balance Lock: {self.balance_lock} | '
            f'Balance: {self.balance} | '
        )
