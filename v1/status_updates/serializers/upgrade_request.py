from django.core.cache import cache
from rest_framework import serializers
from thenewboston.constants.network import CONFIRMATION_VALIDATOR, PRIMARY_VALIDATOR, VERIFY_KEY_LENGTH

from v1.banks.helpers.most_trusted import get_most_trusted_bank
from v1.banks.models.bank import Bank
from v1.cache_tools.cache_keys import BLOCK_QUEUE, CONFIRMATION_BLOCK_QUEUE
from v1.self_configurations.helpers.self_configuration import get_self_configuration
from v1.tasks.upgrade_notices import send_upgrade_notices


class UpgradeRequestSerializer(serializers.Serializer):
    node_identifier = serializers.CharField(max_length=VERIFY_KEY_LENGTH)
    validator_node_identifier = serializers.CharField(max_length=VERIFY_KEY_LENGTH)

    def create(self, validated_data):
        """
        Accept the banks primary validator upgrade request

        If self is currently set as confirmation validator:
        - upgrade self to primary validator
        - clear block queues

        If self is currently set as primary validator, no action is required
        """

        self_configuration = get_self_configuration(exception_class=RuntimeError)

        if self_configuration.node_type == CONFIRMATION_VALIDATOR:
            self_configuration.node_type = PRIMARY_VALIDATOR
            self_configuration.save()
            cache.set(BLOCK_QUEUE, [], None)
            cache.set(CONFIRMATION_BLOCK_QUEUE, {}, None)
            send_upgrade_notices.delay(requesting_banks_node_identifier=validated_data['node_identifier'])

        return self_configuration

    def update(self, instance, validated_data):
        pass

    def validate(self, data):
        """
        Check that self node_identifier matches validator_node_identifier
        - this ensures that the request was intended for self
        """

        self_configuration = get_self_configuration(exception_class=RuntimeError)
        self_node_identifier = self_configuration.node_identifier
        validator_node_identifier = data['validator_node_identifier']

        if self_node_identifier != validator_node_identifier:
            raise serializers.ValidationError(
                f'self_node_identifier of {self_node_identifier} does not match '
                f'validator_node_identifier of {validator_node_identifier}'
            )

        return data

    @staticmethod
    def validate_node_identifier(node_identifier):
        """
        Validate node_identifier is that of most trusted bank
        """

        bank = Bank.objects.filter(node_identifier=node_identifier).first()

        if not bank:
            raise serializers.ValidationError('Bank with that node identifier does not exists')

        if bank != get_most_trusted_bank():
            raise serializers.ValidationError('Bank is not the most trusted')

        return node_identifier
