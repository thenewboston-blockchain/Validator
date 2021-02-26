from django.core.cache import cache
from rest_framework import serializers
from thenewboston.constants.network import BALANCE_LOCK_LENGTH, MAX_POINT_VALUE, VERIFY_KEY_LENGTH
from thenewboston.serializers.network_block import NetworkBlockSerializer

from thenewboston_validator.cache_tools.cache_keys import get_queued_confirmation_block_cache_key, get_valid_confirmation_block_cache_key
from thenewboston_validator.cache_tools.queued_confirmation_blocks import add_queued_confirmation_block


class UpdatedBalanceSerializer(serializers.Serializer):
    account_number = serializers.CharField(max_length=VERIFY_KEY_LENGTH)
    balance = serializers.IntegerField(min_value=0, max_value=MAX_POINT_VALUE)
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
        """Add a confirmation block to the queue"""
        add_queued_confirmation_block(confirmation_block=self.initial_data)
        return validated_data['block_identifier']

    def update(self, instance, validated_data):
        pass

    def validate(self, data):
        """Check that confirmation block is unique (based on block_identifier)"""
        block_identifier = data['block_identifier']

        queued_confirmation_block_cache_key = get_queued_confirmation_block_cache_key(block_identifier=block_identifier)
        valid_confirmation_block_cache_key = get_valid_confirmation_block_cache_key(block_identifier=block_identifier)

        # TODO: Checking for the existence of the key is fine, however .has_key() causes PEP8 warnings due to Pythons
        # TODO: deprecated has_key function

        if cache.get(queued_confirmation_block_cache_key):
            raise serializers.ValidationError('Queued confirmation block with that block_identifier already exists')

        if cache.get(valid_confirmation_block_cache_key):
            raise serializers.ValidationError('Valid confirmation block with that block_identifier already exists')

        return data

    @staticmethod
    def validate_updated_balances(updated_balances):
        """Verify that only 1 updated balance includes a balance_lock (the sender)"""
        account_numbers = {i['account_number'] for i in updated_balances}

        if len(account_numbers) != len(updated_balances):
            raise serializers.ValidationError(
                'Length of unique account numbers should match length of updated_balances'
            )

        balance_locks = [i['balance_lock'] for i in updated_balances if i.get('balance_lock')]

        if len(balance_locks) != 1:
            raise serializers.ValidationError('Should only contain 1 balance lock')

        return updated_balances
