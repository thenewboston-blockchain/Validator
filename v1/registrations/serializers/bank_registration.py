from rest_framework import serializers

from v1.banks.models.bank import Bank
from v1.network.constants.models import ACCEPTED, PENDING
from v1.network.serializers.network_transaction import NetworkTransactionSerializer
from v1.network.utils.serializers import all_field_names
from v1.self_configurations.helpers.self_configuration import get_self_configuration
from ..models.bank_registration import BankRegistration


class BankRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = BankRegistration
        fields = '__all__'
        read_only_fields = all_field_names(BankRegistration)


class BankRegistrationSerializerCreate(serializers.Serializer):
    signature = serializers.CharField(max_length=256, required=True)
    txs = NetworkTransactionSerializer(many=True, required=True)
    verifying_key_hex = serializers.CharField(max_length=256, required=True)

    def create(self, validated_data):
        """
        Create bank registration
        """

        tx_details = validated_data['txs']
        txs = tx_details['txs']

        # TODO: Create Bank if it doesn't exist
        # TODO: Set proper Bank FK and IP address below

        bank_registration = BankRegistration.objects.create(
            bank=None,
            fee=tx_details['validator_registration_fee'],
            identifier=validated_data['verifying_key_hex'],
            ip_address=None,
            status=ACCEPTED
        )

        # TODO: Save Txs (there's only 1) to transaction log and update balance sheet
        print(txs)

        return bank_registration

    def update(self, instance, validated_data):
        raise RuntimeError('Method unavailable')

    @staticmethod
    def _validate_tx_exists(*, amount, recipient, txs):
        """
        Check for the existence of a Tx
        """

        tx = next((tx for tx in txs if tx.get('amount') == amount and tx.get('recipient') == recipient), None)
        if not tx:
            raise serializers.ValidationError({
                'error_message': 'Tx not found',
                'expected_amount': amount,
                'expected_recipient': recipient
            })

    @staticmethod
    def validate_verifying_key_hex(verifying_key_hex):
        """
        Check if bank already exists
        Check for existing pending registration
        """

        if Bank.objects.filter(identifier=verifying_key_hex).exists():
            raise serializers.ValidationError('Bank already exists')

        if BankRegistration.objects.filter(identifier=verifying_key_hex, status=PENDING).exists():
            raise serializers.ValidationError('Pending registration already exists')

        return verifying_key_hex

    def validate_txs(self, txs):
        """
        Verify that correct payment exist
        Verify that there are no extra payments
        """

        self_configuration = get_self_configuration(exception_class=RuntimeError)
        validator_registration_fee = self_configuration.registration_fee

        if validator_registration_fee == 0:

            if txs:
                raise serializers.ValidationError('No Txs required')

            return {
                'txs': txs,
                'validator_registration_fee': validator_registration_fee
            }

        if not txs:
            raise serializers.ValidationError('No Tx')

        if len(txs) > 1:
            raise serializers.ValidationError('Only 1 Tx required')

        self._validate_tx_exists(
            amount=validator_registration_fee,
            recipient=self_configuration.identifier,
            txs=txs
        )

        return {
            'txs': txs,
            'validator_registration_fee': validator_registration_fee
        }
