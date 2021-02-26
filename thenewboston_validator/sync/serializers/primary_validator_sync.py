from rest_framework import serializers
from thenewboston.constants.network import PRIMARY_VALIDATOR

from thenewboston_validator.validators.models.validator import Validator


class PrimaryValidatorSyncSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Validator

    @staticmethod
    def validate_node_type(node_type):
        """Validate that node is configured as a primary validator"""
        if node_type != PRIMARY_VALIDATOR:
            raise serializers.ValidationError('Node is not configured as a primary validator')

        return node_type
