from rest_framework import serializers
from thenewboston.constants.network import BANK, HEAD_HASH_LENGTH, PROTOCOL_CHOICES, VERIFY_KEY_LENGTH

from v1.self_configurations.helpers.self_configuration import get_self_configuration
from v1.self_configurations.serializers.self_configuration import SelfConfigurationSerializer

"""
The BankConfigurationSerializer is used to ensure that a bank is properly configured
- used during bank registration process by both the primary and backup validators
"""


class PrimaryValidatorSerializer(serializers.Serializer):
    account_number = serializers.CharField(max_length=VERIFY_KEY_LENGTH)
    default_transaction_fee = serializers.DecimalField(max_digits=32, decimal_places=16)
    ip_address = serializers.IPAddressField(protocol='both')
    network_identifier = serializers.CharField(max_length=VERIFY_KEY_LENGTH)
    port = serializers.IntegerField(max_value=65535, min_value=0, required=False)
    protocol = serializers.ChoiceField(choices=PROTOCOL_CHOICES)
    registration_fee = serializers.DecimalField(max_digits=32, decimal_places=16)
    root_account_file = serializers.URLField()
    root_account_file_hash = serializers.CharField(max_length=HEAD_HASH_LENGTH)
    seed_block_hash = serializers.CharField(max_length=HEAD_HASH_LENGTH)
    version = serializers.CharField(max_length=32)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def validate(self, data):
        """
        Validate that banks primary validator matches self primary validator
        - trust excluded
        """

        self_configuration = get_self_configuration(exception_class=RuntimeError)
        self_configuration = SelfConfigurationSerializer(self_configuration).data

        for key, value in self_configuration.items():

            if key in ['node_type', 'primary_validator']:
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


class BankConfigurationSerializer(serializers.Serializer):
    primary_validator = PrimaryValidatorSerializer()
    account_number = serializers.CharField(max_length=VERIFY_KEY_LENGTH)
    default_transaction_fee = serializers.DecimalField(max_digits=32, decimal_places=16)
    ip_address = serializers.IPAddressField(protocol='both')
    network_identifier = serializers.CharField(max_length=VERIFY_KEY_LENGTH)
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

        if node_type != BANK:
            raise serializers.ValidationError('Incorrect node_type')

        return node_type