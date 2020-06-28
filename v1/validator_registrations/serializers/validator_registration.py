from django.core.cache import cache
from rest_framework import serializers
from thenewboston.constants.network import PENDING, PROTOCOL_CHOICES, VERIFY_KEY_LENGTH
from thenewboston.serializers.network_block import NetworkBlockSerializer
from thenewboston.transactions.validation import validate_transaction_exists
from thenewboston.utils.fields import all_field_names

from v1.cache_tools.cache_keys import get_pending_validator_registration_pk_cache_key
from v1.self_configurations.helpers.self_configuration import get_self_configuration
from v1.validators.models.validator import Validator
from ..models.validator_registration import ValidatorRegistration


class ValidatorRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ValidatorRegistration
        fields = '__all__'
        read_only_fields = all_field_names(ValidatorRegistration)


class ValidatorRegistrationSerializerCreate(serializers.Serializer):
    block = NetworkBlockSerializer()
    ip_address = serializers.IPAddressField(protocol='both')
    node_identifier = serializers.CharField(max_length=VERIFY_KEY_LENGTH)
    pk = serializers.UUIDField(format='hex_verbose')
    port = serializers.IntegerField(max_value=65535, min_value=0, required=False)
    protocol = serializers.ChoiceField(choices=PROTOCOL_CHOICES)
    validator_node_identifier = serializers.CharField(max_length=VERIFY_KEY_LENGTH)
    version = serializers.CharField(max_length=32)

    def create(self, validated_data):
        """
        Create validator registration
        """

        block_validation_dict = validated_data['block']
        block = block_validation_dict['block']
        self_registration_fee = block_validation_dict['self_registration_fee']

        ip_address = validated_data['ip_address']
        pk = validated_data['pk']
        port = validated_data['port']
        protocol = validated_data['protocol']

        validator_registration = ValidatorRegistration.objects.create(
            validator=None,
            fee=self_registration_fee,
            ip_address=ip_address,
            node_identifier=validated_data['node_identifier'],
            pk=str(pk),
            port=port,
            protocol=protocol,
            registration_block_signature=block['signature'],
            status=PENDING
        )

        validator_registration_cache_key = get_pending_validator_registration_pk_cache_key(
            block_signature=block['signature']
        )
        cache.set(validator_registration_cache_key, str(pk), None)

        return validator_registration

    def update(self, instance, validated_data):
        raise RuntimeError('Method unavailable')

    def validate(self, data):
        """
        Validate IP address
        """

        ip_address = data['ip_address']
        port = data['port']

        if Validator.objects.filter(ip_address=ip_address, port=port).exists():
            raise serializers.ValidationError('Validator at that location already exists')

        if ValidatorRegistration.objects.filter(ip_address=ip_address, port=port, status=PENDING).exists():
            raise serializers.ValidationError('Validator at that location already has pending registration')

        return data

    @staticmethod
    def validate_block(block):
        """
        Verify that correct payment exist
        Verify that there are no extra payments
        """

        self_configuration = get_self_configuration(exception_class=RuntimeError)

        primary_validator = self_configuration.primary_validator
        self_registration_fee = self_configuration.registration_fee
        is_primary_validator = bool(not primary_validator)

        txs = block['message']['txs']

        if not txs:
            raise serializers.ValidationError('No Tx')

        validate_transaction_exists(
            amount=self_registration_fee,
            error=serializers.ValidationError,
            recipient=self_configuration.account_number,
            txs=txs
        )

        if is_primary_validator:

            if len(txs) > 1:
                raise serializers.ValidationError('Only 1 Tx required when registering with primary validator')

        if not is_primary_validator:

            validate_transaction_exists(
                amount=primary_validator.registration_fee,
                error=serializers.ValidationError,
                recipient=primary_validator.account_number,
                txs=txs
            )

            if len(txs) > 2:
                raise serializers.ValidationError('Only 2 Txs required when registering with confirmation validators')

        return {
            'block': block,
            'self_registration_fee': self_registration_fee
        }

    @staticmethod
    def validate_node_identifier(node_identifier):
        """
        Check if validator already exists
        Check for existing pending registration
        """

        if Validator.objects.filter(node_identifier=node_identifier).exists():
            raise serializers.ValidationError('Validator with that node identifier already exists')

        if ValidatorRegistration.objects.filter(node_identifier=node_identifier, status=PENDING).exists():
            raise serializers.ValidationError('Validator with that node identifier already has pending registration')

        return node_identifier
