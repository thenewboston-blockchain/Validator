from django.core.cache import cache
from rest_framework import serializers
from thenewboston.constants.network import BALANCE_LOCK_LENGTH, VERIFY_KEY_LENGTH
from thenewboston.serializers.network_block import NetworkBlockSerializer

from v1.cache_tools.cache_keys import CONFIRMATION_BLOCK_QUEUE


class UpdatedBalanceSerializer(serializers.Serializer):
    account_number = serializers.CharField(max_length=VERIFY_KEY_LENGTH)
    balance = serializers.DecimalField(max_digits=32, decimal_places=16)
    balance_lock = serializers.CharField(max_length=BALANCE_LOCK_LENGTH, required=False)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ConfirmationBlockSerializerCreate(serializers.Serializer):
    block = NetworkBlockSerializer()
    block_identifier = serializers.CharField(max_length=VERIFY_KEY_LENGTH)
    updated_balances = UpdatedBalanceSerializer(many=True)

    def create(self, validated_data):
        """
        Add a confirmation block to the queue
        """

        block_identifier = validated_data['block_identifier']
        confirmation_block_queue = cache.get(CONFIRMATION_BLOCK_QUEUE)
        confirmation_block_queue[block_identifier] = self.initial_data
        cache.set(CONFIRMATION_BLOCK_QUEUE, confirmation_block_queue, None)

        return block_identifier

    def update(self, instance, validated_data):
        pass

    def validate(self, data):
        """
        Check that confirmation block is unique (based on block_identifier)
        """

        block_identifier = data['block_identifier']
        confirmation_block_queue = cache.get(CONFIRMATION_BLOCK_QUEUE)

        if confirmation_block_queue.get(block_identifier):
            raise serializers.ValidationError('Confirmation block with that block_identifier already exists')

        return data

    @staticmethod
    def validate_updated_balances(updated_balances):
        """
        Verify that only 1 updated balance includes a balance_lock (the sender)
        """

        account_numbers = {i['account_number'] for i in updated_balances}

        if len(account_numbers) != len(updated_balances):
            raise serializers.ValidationError(
                'Length of unique account numbers should match length of updated_balances'
            )

        balance_locks = [i['balance_lock'] for i in updated_balances if i.get('balance_lock')]

        if len(balance_locks) != 1:
            raise serializers.ValidationError('Should only contain 1 balance lock')

        return updated_balances
