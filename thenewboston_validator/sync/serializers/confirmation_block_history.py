from rest_framework import serializers
from thenewboston.constants.network import PRIMARY_VALIDATOR, VERIFY_KEY_LENGTH

from thenewboston_validator.cache_tools.valid_confirmation_blocks import get_valid_confirmation_block
from thenewboston_validator.self_configurations.helpers.self_configuration import get_self_configuration
from thenewboston_validator.tasks.confirmation_block_history import send_confirmation_block_history
from thenewboston_validator.validators.models.validator import Validator


class ConfirmationBlockHistorySerializer(serializers.Serializer):
    block_identifier = serializers.CharField(max_length=VERIFY_KEY_LENGTH)
    node_identifier = serializers.CharField(max_length=VERIFY_KEY_LENGTH)

    def create(self, validated_data):
        """Send historical confirmation blocks (starting with the block_identifier) to the confirmation validator"""
        block_identifier = validated_data['block_identifier']
        validator = validated_data['node_identifier']

        send_confirmation_block_history.delay(
            block_identifier=block_identifier,
            ip_address=validator.ip_address,
            port=validator.port,
            protocol=validator.protocol
        )

        return validated_data

    def update(self, instance, validated_data):
        pass

    def validate(self, data):
        """Validate self is configured as primary validator"""
        self_configuration = get_self_configuration(exception_class=RuntimeError)

        if self_configuration.node_type != PRIMARY_VALIDATOR:
            raise serializers.ValidationError('Node is not configured as a primary validator')

        return data

    @staticmethod
    def validate_block_identifier(block_identifier):
        """Validate confirmation block matching block_identifier exists"""
        valid_confirmation_block = get_valid_confirmation_block(block_identifier=block_identifier)

        if not valid_confirmation_block:
            raise serializers.ValidationError('Confirmation block with that block identifier does not exists')

        return block_identifier

    @staticmethod
    def validate_node_identifier(node_identifier):
        """Validate node_identifier is from a connected validator"""
        validator = Validator.objects.filter(node_identifier=node_identifier).first()

        if not validator:
            raise serializers.ValidationError('Validator with that node identifier does not exists')

        return validator
