from factory import Faker
from factory.django import DjangoModelFactory
from thenewboston.constants.network import BALANCE_LOCK_LENGTH, MAX_POINT_VALUE, VERIFY_KEY_LENGTH

from ..models.account import Account


class AccountFactory(DjangoModelFactory):
    account_number = Faker('pystr', max_chars=VERIFY_KEY_LENGTH)
    balance = Faker('pyint', max_value=MAX_POINT_VALUE)
    balance_lock = Faker('pystr', max_chars=BALANCE_LOCK_LENGTH)

    class Meta:
        model = Account
