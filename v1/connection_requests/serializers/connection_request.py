from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from thenewboston.constants.network import VERIFY_KEY_LENGTH
from thenewboston.utils.fields import all_field_names

from ..models.connection_request import ConnectionRequest


class ConnectionRequestSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = ConnectionRequest
        read_only_fields = all_field_names(ConnectionRequest)


class ConnectionRequestSerializerCreate(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = ConnectionRequest
        validators = [
            UniqueTogetherValidator(
                queryset=ConnectionRequest.objects.all(),
                fields=['ip_address', 'port']
            )
        ]

    def create(self, validated_data):
        """
        Create connection request and add to queue
        """

        connection_request = ConnectionRequest.objects.create(**validated_data)

        return connection_request

    @staticmethod
    def validate_node_identifier(node_identifier):
        """
        Validate node_identifier length
        """

        if len(node_identifier) != VERIFY_KEY_LENGTH:
            raise serializers.ValidationError(f'node_identifier must be {VERIFY_KEY_LENGTH} characters long')

        return node_identifier
