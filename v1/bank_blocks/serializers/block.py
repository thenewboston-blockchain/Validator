from rest_framework import serializers
from thenewboston.constants.network import PRIMARY_VALIDATOR
from thenewboston.serializers.network_block import NetworkBlockSerializer
from thenewboston.transactions.validation import validate_transaction_exists

from v1.self_configurations.helpers.self_configuration import get_self_configuration


class BlockSerializer(NetworkBlockSerializer):

    def create(self, validated_data):
        raise RuntimeError('Method unavailable')

    def update(self, instance, validated_data):
        raise RuntimeError('Method unavailable')

    def validate(self, data):
        """Verify that correct payment exist for the Primary Validator"""
        data = super(BlockSerializer, self).validate(data)

        account_number = data['account_number']
        message = data['message']
        txs = message['txs']

        self_configuration = get_self_configuration(exception_class=RuntimeError)

        if account_number != self_configuration.account_number:
            validate_transaction_exists(
                amount=self_configuration.default_transaction_fee,
                fee=PRIMARY_VALIDATOR,
                error=serializers.ValidationError,
                recipient=self_configuration.account_number,
                txs=txs
            )

        return data
