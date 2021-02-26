from thenewboston.utils.fields import standard_field_names

from thenewboston_validator.banks.models.bank import Bank
from thenewboston_validator.validators.models.validator import Validator


def create_bank_from_config_data(*, config_data):
    """Create bank from config data"""
    excluded = ['confirmation_expiration', 'trust']
    fields = standard_field_names(Bank)
    data = {field: config_data[field] for field in fields if field not in excluded}
    Bank.objects.create(**data, trust=0)


def create_validator_from_config_data(*, config_data):
    """Create validator from config data"""
    fields = standard_field_names(Validator)
    data = {field: config_data[field] for field in fields if field != 'trust'}
    Validator.objects.create(**data, trust=0)


def update_bank_from_config_data(*, bank, config_data):
    """Update bank from config data"""
    excluded = ['confirmation_expiration', 'trust']
    fields = standard_field_names(Bank)
    data = {field: config_data[field] for field in fields if field not in excluded}
    Bank.objects.filter(pk=bank.pk).update(**data)


def update_validator_from_config_data(*, validator, config_data):
    """Update validator from config data"""
    fields = standard_field_names(Validator)
    data = {field: config_data[field] for field in fields if field != 'trust'}
    Validator.objects.filter(pk=validator.pk).update(**data)
