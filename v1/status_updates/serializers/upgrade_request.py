from rest_framework import serializers
from thenewboston.constants.network import CONFIRMATION_VALIDATOR, VERIFY_KEY_LENGTH

from v1.banks.helpers.most_trusted import get_most_trusted_bank
from v1.banks.models.bank import Bank
from v1.self_configurations.helpers.self_configuration import get_self_configuration


class UpgradeRequestSerializer(serializers.Serializer):
    node_identifier = serializers.CharField(max_length=VERIFY_KEY_LENGTH)
    validator_node_identifier = serializers.CharField(max_length=VERIFY_KEY_LENGTH)

    def create(self, validated_data):
        """
        Upgrade self to primary validator
        """

        # TODO: Upgrade self to primary validator (celery task)
        # TODO: Send notice to bank once complete

        return True

    def update(self, instance, validated_data):
        pass

    def validate(self, data):
        """
        Check that node_type is set to CONFIRMATION_VALIDATOR
        """

        self_configuration = get_self_configuration(exception_class=RuntimeError)

        if self_configuration.node_type != CONFIRMATION_VALIDATOR:
            raise serializers.ValidationError(f'node_type is not {CONFIRMATION_VALIDATOR}')

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
