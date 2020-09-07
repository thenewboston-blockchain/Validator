from thenewboston.utils.fields import standard_field_names

from v1.banks.models.bank import Bank
from v1.validators.models.validator import Validator


def create_bank_from_config_data(*, config_data):
    """
    Create bank from config data
    """

    fields = standard_field_names(Bank)
    data = {field: config_data[field] for field in fields if field != 'trust'}
    Bank.objects.create(**data, trust=0)


def create_validator_from_config_data(*, config_data):
    """
    Create validator from config data
    """

    fields = standard_field_names(Validator)
    data = {field: config_data[field] for field in fields if field != 'trust'}
    Validator.objects.create(**data, trust=0)
