from rest_framework import serializers
from thenewboston.constants.network import CONFIRMATION_VALIDATOR, PRIMARY_VALIDATOR
from thenewboston.serializers.configuration import ConfigurationSerializer
from thenewboston.serializers.primary_validator import PrimaryValidatorSerializer

from v1.self_configurations.helpers.self_configuration import get_self_configuration
from v1.self_configurations.serializers.self_configuration import SelfConfigurationSerializer
from .validator import ValidatorSerializer

"""
The ValidatorConfigurationSerializer is used to ensure that the requesting validator is properly configured
- used during validator registration process by both the primary and confirmation validators
"""


class ValidatorPrimaryValidatorSerializer(PrimaryValidatorSerializer):

    def validate(self, data):
        """
        Validate that requesting nodes primary validator matches self primary validator
        """

        self_configuration = get_self_configuration(exception_class=RuntimeError)
        primary_validator = self_configuration.primary_validator
        is_primary_validator = bool(not primary_validator)

        if is_primary_validator:
            primary_validator_configuration = SelfConfigurationSerializer(self_configuration).data
        else:
            primary_validator_configuration = ValidatorSerializer(primary_validator).data

        if primary_validator_configuration['node_type'] != PRIMARY_VALIDATOR:
            raise serializers.ValidationError('Incorrect node_type on primary validator')

        for key, primary_validator_value in primary_validator_configuration.items():

            if key in ['node_type', 'primary_validator', 'trust']:
                continue

            requesting_node_value = data.get(key)

            if not requesting_node_value:
                raise serializers.ValidationError(f'{key} not found on requesting validators primary validator')

            if str(requesting_node_value) != str(primary_validator_value):
                raise serializers.ValidationError(
                    f'Inconsistent primary validator settings for {key}. '
                    f'Requesting nodes value of {requesting_node_value} '
                    f'does not match expected value of {primary_validator_value}.'
                )

        return data


class ValidatorConfigurationSerializer(ConfigurationSerializer):
    primary_validator = ValidatorPrimaryValidatorSerializer()

    @staticmethod
    def validate_node_type(node_type):
        """
        Validate node type
        """

        if node_type not in [CONFIRMATION_VALIDATOR, PRIMARY_VALIDATOR]:
            raise serializers.ValidationError('Incorrect node_type')

        return node_type
