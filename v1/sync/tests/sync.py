import pytest
from rest_framework import serializers
from thenewboston.constants.network import CONFIRMATION_VALIDATOR, PRIMARY_VALIDATOR

from ..serializers.confirmation_block_history import ConfirmationBlockHistorySerializer
from ..serializers.primary_validator_sync import PrimaryValidatorSyncSerializer


def test_validate_node_type_success():
    assert PrimaryValidatorSyncSerializer.validate_node_type(PRIMARY_VALIDATOR) == PRIMARY_VALIDATOR


def test_validate_node_type_failed():
    with pytest.raises(serializers.ValidationError) as e:
        PrimaryValidatorSyncSerializer.validate_node_type(CONFIRMATION_VALIDATOR)

    assert 'Node is not configured as a primary validator' in str(e)


def test_validate_node_identifier_success(encoded_account_number, validator):
    assert ConfirmationBlockHistorySerializer.validate_node_identifier(
        node_identifier=encoded_account_number) == validator


def test_validate_node_identifier_failed(random_encoded_account_number):
    with pytest.raises(serializers.ValidationError) as e:
        ConfirmationBlockHistorySerializer.validate_node_identifier(random_encoded_account_number)

    assert 'Validator with that node identifier does not exists' in str(e)
