from rest_framework import serializers
from thenewboston.constants.network import HEAD_HASH_LENGTH, PROTOCOL_CHOICES, VALIDATOR, VERIFY_KEY_LENGTH

from v1.self_configurations.helpers.self_configuration import get_self_configuration
from v1.self_configurations.serializers.self_configuration import SelfConfigurationSerializer
from .validator import ValidatorSerializer

"""
The ValidatorConfigurationSerializer is used to ensure that the requesting validator is properly configured
- used during validator registration process by both the primary and confirmation validators
"""


class PrimaryValidatorSerializer(serializers.Serializer):
    account_number = serializers.CharField(max_length=VERIFY_KEY_LENGTH)
    default_transaction_fee = serializers.DecimalField(max_digits=32, decimal_places=16)
    ip_address = serializers.IPAddressField(protocol='both')
    node_identifier = serializers.CharField(max_length=VERIFY_KEY_LENGTH)
    port = serializers.IntegerField(max_value=65535, min_value=0, required=False)
    protocol = serializers.ChoiceField(choices=PROTOCOL_CHOICES)
    registration_fee = serializers.DecimalField(max_digits=32, decimal_places=16)
    root_account_file = serializers.URLField()
    root_account_file_hash = serializers.CharField(max_length=HEAD_HASH_LENGTH)
    seed_block_identifier = serializers.CharField(max_length=HEAD_HASH_LENGTH)
    version = serializers.CharField(max_length=32)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def validate(self, data):
        """
        Validate that requesting validators primary validator matches self primary validator
        - trust excluded
        """

        self_configuration = get_self_configuration(exception_class=RuntimeError)
        primary_validator = self_configuration.primary_validator
        is_primary_validator = bool(not primary_validator)

        if is_primary_validator:
            primary_validator_configuration = SelfConfigurationSerializer(self_configuration).data
        else:
            primary_validator_configuration = ValidatorSerializer(primary_validator).data

        for key, primary_validator_value in primary_validator_configuration.items():

            if key in ['node_type', 'primary_validator', 'trust']:
                continue

            requesting_validator_value = data.get(key)

            if not requesting_validator_value:
                raise serializers.ValidationError(f'{key} not found on requesting validators primary validator')

            if str(requesting_validator_value) != str(primary_validator_value):
                raise serializers.ValidationError(
                    f'Inconsistent primary validator settings for {key}. '
                    f'Requesting validator value of {requesting_validator_value} '
                    f'does not match expected value of {primary_validator_value}.'
                )

        return data


class ValidatorConfigurationSerializer(serializers.Serializer):
    primary_validator = PrimaryValidatorSerializer()
    account_number = serializers.CharField(max_length=VERIFY_KEY_LENGTH)
    default_transaction_fee = serializers.DecimalField(max_digits=32, decimal_places=16)
    ip_address = serializers.IPAddressField(protocol='both')
    node_identifier = serializers.CharField(max_length=VERIFY_KEY_LENGTH)
    node_type = serializers.CharField(max_length=4)
    port = serializers.IntegerField(max_value=65535, min_value=0, required=False)
    protocol = serializers.ChoiceField(choices=PROTOCOL_CHOICES)
    registration_fee = serializers.DecimalField(max_digits=32, decimal_places=16)
    version = serializers.CharField(max_length=32)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    @staticmethod
    def validate_node_type(node_type):
        """
        Validate node type
        """

        if node_type != VALIDATOR:
            raise serializers.ValidationError('Incorrect node_type')

        return node_type
