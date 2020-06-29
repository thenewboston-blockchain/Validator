from rest_framework import serializers
from thenewboston.constants.network import BANK
from thenewboston.serializers.configuration import ConfigurationSerializer
from thenewboston.serializers.primary_validator import PrimaryValidatorSerializer

from v1.self_configurations.helpers.self_configuration import get_self_configuration
from v1.self_configurations.serializers.self_configuration import SelfConfigurationSerializer

"""
The BankConfigurationSerializer is used to ensure that a bank is properly configured
- used during bank registration process by both the primary and confirmation validators
"""


class BankPrimaryValidatorSerializer(PrimaryValidatorSerializer):

    def validate(self, data):
        """
        Validate that banks primary validator matches self primary validator
        """

        self_configuration = get_self_configuration(exception_class=RuntimeError)
        self_configuration = SelfConfigurationSerializer(self_configuration).data

        for key, value in self_configuration.items():

            if key in ['node_type', 'primary_validator', 'trust']:
                continue

            bank_value = data.get(key)

            if not bank_value:
                raise serializers.ValidationError(f'{key} not found on banks primary validator')

            if str(bank_value) != str(value):
                raise serializers.ValidationError(
                    f'Inconsistent primary validator settings for {key}. '
                    f'Bank value of {bank_value} does not match validator value of {value}.'
                )

        return data


class BankConfigurationSerializer(ConfigurationSerializer):
    primary_validator = BankPrimaryValidatorSerializer()

    @staticmethod
    def validate_node_type(node_type):
        """
        Validate node type
        """

        if node_type != BANK:
            raise serializers.ValidationError('Incorrect node_type')

        return node_type
