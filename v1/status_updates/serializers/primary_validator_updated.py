from rest_framework import serializers
from thenewboston.constants.network import PROTOCOL_CHOICES, VERIFY_KEY_LENGTH

from v1.banks.helpers.most_trusted import get_most_trusted_bank
from v1.banks.models.bank import Bank


class PrimaryValidatorUpdatedSerializer(serializers.Serializer):
    ip_address = serializers.IPAddressField(protocol='both')
    node_identifier = serializers.CharField(max_length=VERIFY_KEY_LENGTH)
    port = serializers.IntegerField(allow_null=True, max_value=65535, min_value=0, required=False)
    protocol = serializers.ChoiceField(choices=PROTOCOL_CHOICES)

    def create(self, validated_data):
        """
        Sync to the new primary validator
        """

        bank = validated_data['node_identifier']
        ip_address = validated_data['ip_address']
        port = validated_data['port']
        protocol = validated_data['protocol']

        if bank == get_most_trusted_bank():
            # TODO: Sync to the new primary validator
            print(ip_address, port, protocol)
        else:
            bank.delete()
            raise serializers.ValidationError('Bank is not the most trusted')

        return True

    def update(self, instance, validated_data):
        pass

    @staticmethod
    def validate_node_identifier(node_identifier):
        """
        Validate node_identifier is from bank
        """

        bank = Bank.objects.filter(node_identifier=node_identifier).first()

        if not bank:
            raise serializers.ValidationError('Bank with that node identifier does not exists')

        return bank
