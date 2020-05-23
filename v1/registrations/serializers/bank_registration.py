from rest_framework import serializers
from thenewboston.constants.network import PENDING
from thenewboston.constants.network import PROTOCOL_CHOICES
from thenewboston.serializers.network_transaction import NetworkTransactionSerializer
from thenewboston.transactions.validation import validate_transaction_exists
from thenewboston.utils.fields import all_field_names
from thenewboston.utils.format import format_address
from thenewboston.utils.network import fetch

from v1.banks.models.bank import Bank
from v1.self_configurations.helpers.self_configuration import get_self_configuration
from ..models.bank_registration import BankRegistration


class BankRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = BankRegistration
        fields = '__all__'
        read_only_fields = all_field_names(BankRegistration)


class BankRegistrationSerializerCreate(serializers.Serializer):
    account_number = serializers.CharField(max_length=64)
    ip_address = serializers.IPAddressField(protocol='both')
    port = serializers.IntegerField(max_value=65535, min_value=0, required=False)
    protocol = serializers.ChoiceField(choices=PROTOCOL_CHOICES)
    signature = serializers.CharField(max_length=128)
    txs = NetworkTransactionSerializer(many=True)

    def create(self, validated_data):
        """
        Create bank registration
        """

        ip_address = validated_data['ip_address']
        port = validated_data['port']
        protocol = validated_data['protocol']
        tx_details = validated_data['txs']
        txs = tx_details['txs']

        bank_registration = BankRegistration.objects.create(
            account_number=validated_data['account_number'],
            bank=None,
            fee=tx_details['validator_registration_fee'],
            ip_address=ip_address,
            port=port,
            protocol=protocol,
            status=PENDING
        )

        # TODO: Save Txs (there's only 1) to transaction log and update balance sheet
        print(txs)

        # TODO: Do background check on Bank, if good update status to ACCEPTED (celery task)
        # TODO: If ACCEPTED create Bank if it doesn't exist as well
        # TODO: Set proper Bank FK on BankRegistration as well
        # TODO: Send a request to the bank letting them know of the results either way
        address = format_address(ip_address=ip_address, port=port, protocol=protocol)
        config_address = f'{address}/config'
        print(config_address)

        results = fetch(url=config_address, headers={})

        # TODO: Check that configs match, if so approve (if not decline)
        # TODO: Just send the serialized BankRegistration object with the updated status
        print(results)

        return bank_registration

    def update(self, instance, validated_data):
        raise RuntimeError('Method unavailable')

    def validate(self, data):
        """
        Validate IP address
        """

        ip_address = data['ip_address']
        port = data['port']

        if Bank.objects.filter(ip_address=ip_address, port=port).exists():
            raise serializers.ValidationError('Bank at that location already exists')

        if BankRegistration.objects.filter(ip_address=ip_address, port=port, status=PENDING).exists():
            raise serializers.ValidationError('Bank at that location already has pending registration')

        return data

    @staticmethod
    def validate_account_number(account_number):
        """
        Check if bank already exists
        Check for existing pending registration
        """

        if Bank.objects.filter(account_number=account_number).exists():
            raise serializers.ValidationError('Bank with that account number already exists')

        if BankRegistration.objects.filter(account_number=account_number, status=PENDING).exists():
            raise serializers.ValidationError('Bank with that account number already has pending registration')

        return account_number

    @staticmethod
    def validate_txs(txs):
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

        validate_transaction_exists(
            amount=validator_registration_fee,
            error=serializers.ValidationError,
            recipient=self_configuration.identifier,
            txs=txs
        )

        return {
            'txs': txs,
            'validator_registration_fee': validator_registration_fee
        }
