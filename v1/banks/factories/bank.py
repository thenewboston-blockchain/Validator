import pytz
from factory import Faker
from thenewboston.factories.network_node import NetworkNodeFactory

from ..models.bank import Bank


class BankFactory(NetworkNodeFactory):
    confirmation_expiration = Faker('date_time', tzinfo=pytz.utc)
    trust = Faker(
        'pyfloat',
        left_digits=3,
        right_digits=2,
        min_value=0,
        max_value=100,
    )

    class Meta:
        model = Bank
