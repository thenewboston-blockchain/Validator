from rest_framework import serializers
from thenewboston.utils.fields import all_field_names

from ..models.connection_request import ConnectionRequest


class ConnectionRequestSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = ConnectionRequest
        read_only_fields = all_field_names(ConnectionRequest)
