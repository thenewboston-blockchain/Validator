from factory import DjangoModelFactory, Faker
from thenewboston.constants.network import BALANCE_LOCK_LENGTH, VERIFY_KEY_LENGTH

from ..models.account import Account


class AccountFactory(DjangoModelFactory):
    account_number = Faker('pystr', max_chars=VERIFY_KEY_LENGTH)
    balance = Faker(
        'pyfloat',
        left_digits=16,
        right_digits=16,
        min_value=0,
    )
    balance_lock = Faker('pystr', max_chars=BALANCE_LOCK_LENGTH)

    class Meta:
        model = Account
