import logging

from django.core.cache import cache
from django.db import transaction
from rest_framework import serializers
from thenewboston.constants.network import (
    CONFIRMATION_VALIDATOR,
    PENDING,
    PRIMARY_VALIDATOR,
    PROTOCOL_CHOICES,
    VERIFY_KEY_LENGTH
)
from thenewboston.serializers.network_block import NetworkBlockSerializer
from thenewboston.transactions.validation import validate_transaction_exists
from thenewboston.utils.fields import all_field_names

from v1.cache_tools.cache_keys import BLOCK_QUEUE, get_pending_validator_registration_pk_cache_key
from v1.self_configurations.helpers.self_configuration import get_self_configuration
from v1.tasks.blocks import process_block_queue
from v1.tasks.signed_requests import send_signed_post_request
from v1.validators.models.validator import Validator
from ..models.validator_registration import ValidatorRegistration

logger = logging.getLogger('thenewboston')


class ValidatorRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ValidatorRegistration
        fields = '__all__'
        read_only_fields = all_field_names(ValidatorRegistration)


class ValidatorRegistrationSerializerCreate(serializers.Serializer):
    block = NetworkBlockSerializer()
    pk = serializers.UUIDField(format='hex_verbose')
    signing_nid = serializers.CharField(max_length=VERIFY_KEY_LENGTH)

    # Source validator
    source_ip_address = serializers.IPAddressField(protocol='both')
    source_node_identifier = serializers.CharField(max_length=VERIFY_KEY_LENGTH)
    source_port = serializers.IntegerField(max_value=65535, min_value=0, required=False)
    source_protocol = serializers.ChoiceField(choices=PROTOCOL_CHOICES)

    # Target validator
    target_ip_address = serializers.IPAddressField(protocol='both')
    target_node_identifier = serializers.CharField(max_length=VERIFY_KEY_LENGTH)
    target_port = serializers.IntegerField(max_value=65535, min_value=0, required=False)
    target_protocol = serializers.ChoiceField(choices=PROTOCOL_CHOICES)

    def __init__(self, **kwargs):
        """
        Determine if self is source or target validator
        Also determines if self is primary validator
        """

        self.is_source = bool(kwargs['data']['signing_nid'] == kwargs['data'].get('source_node_identifier'))
        self.is_target = bool(kwargs['data']['signing_nid'] == kwargs['data'].get('target_node_identifier'))

        if len([i for i in [self.is_source, self.is_target] if i]) != 1:
            raise serializers.ValidationError('Unable to determine source or target')

        self.config = get_self_configuration(exception_class=RuntimeError)
        self.primary_validator = (
            self.config if self.config.node_type == PRIMARY_VALIDATOR else self.config.primary_validator
        )
        self.is_target_primary_validator = bool(
            kwargs['data'].get('target_node_identifier') == self.primary_validator.node_identifier
        )

        super().__init__(**kwargs)

    def create(self, validated_data):
        """
        Create validator registration
        If source, send to target
        If target:
        - if CV, send to PV
        - if PV, add block to block queue
        """

        block = self.initial_data['block']

        pk = validated_data['pk']
        target_ip_address = validated_data['target_ip_address']
        target_port = validated_data['target_port']
        target_protocol = validated_data['target_protocol']

        try:
            with transaction.atomic():
                validator_registration = ValidatorRegistration.objects.create(
                    pk=str(pk),
                    registration_block_signature=block['signature'],
                    source_ip_address=validated_data['source_ip_address'],
                    source_node_identifier=validated_data['source_node_identifier'],
                    source_port=validated_data['source_port'],
                    source_protocol=validated_data['source_protocol'],
                    status=PENDING,
                    target_ip_address=target_ip_address,
                    target_node_identifier=validated_data['target_node_identifier'],
                    target_port=target_port,
                    target_protocol=target_protocol,
                    validator=None
                )

                if self.is_source:
                    send_signed_post_request.delay(
                        data=self.context['request'].data,
                        ip_address=target_ip_address,
                        port=target_port,
                        protocol=target_protocol,
                        url_path='/validator_registrations'
                    )

                if self.is_target:

                    if self.config.node_type == CONFIRMATION_VALIDATOR:
                        # TODO: Need to send block through bank
                        pass

                    if self.config.node_type == PRIMARY_VALIDATOR:
                        # TODO: Clean up
                        queue = cache.get(BLOCK_QUEUE)

                        if queue:
                            queue.append(block)
                        else:
                            queue = [block]

                        cache.set(BLOCK_QUEUE, queue, None)
                        process_block_queue.delay()

        except Exception as e:
            logger.exception(e)
            raise serializers.ValidationError(e)

        validator_registration_cache_key = get_pending_validator_registration_pk_cache_key(
            block_signature=block['signature']
        )
        cache.set(validator_registration_cache_key, str(pk), None)

        return validator_registration

    def update(self, instance, validated_data):
        raise RuntimeError('Method unavailable')

    def validate(self, data):
        """
        Check IP address and port to see if validator or pending registration already exists
        """

        if self.is_source:
            ip_address = data['target_ip_address']
            port = data['target_port']

            if ValidatorRegistration.objects.filter(
                target_ip_address=ip_address,
                target_port=port,
                status=PENDING
            ).exists():
                raise serializers.ValidationError('Validator at that location already has pending registration')

        else:
            ip_address = data['target_ip_address']
            port = data['target_port']

            if ValidatorRegistration.objects.filter(
                source_ip_address=ip_address,
                source_port=port,
                status=PENDING
            ).exists():
                raise serializers.ValidationError('Validator at that location already has pending registration')

        if Validator.objects.filter(
            ip_address=ip_address,
            port=port
        ).exclude(
            self_configurations__primary_validator__ip_address=ip_address,
            self_configurations__primary_validator__port=port
        ).exists():
            raise serializers.ValidationError('Validator at that location already exists')

        return data

    def validate_block(self, block):
        """
        Verify that correct payment exist
        Verify that there are no extra payments

        If target is primary validator, only one payment should exist:
        - PV registration fee

        If target is confirmation validator, two payments should exist:
        - CV registration fee
        - PV transaction fee
        """

        txs = block['message']['txs']

        if not txs:
            raise serializers.ValidationError('No Tx')

        if self.is_target_primary_validator:
            validate_transaction_exists(
                amount=self.primary_validator.registration_fee,
                error=serializers.ValidationError,
                recipient=self.primary_validator.account_number,
                txs=txs
            )

            if len(txs) > 1:
                raise serializers.ValidationError('Only 1 Tx required when registering with primary validator')

        if not self.is_target_primary_validator:
            validate_transaction_exists(
                amount=self.primary_validator.default_transaction_fee,
                error=serializers.ValidationError,
                recipient=self.primary_validator.account_number,
                txs=txs
            )

            if self.is_target:
                validate_transaction_exists(
                    amount=self.config.registration_fee,
                    error=serializers.ValidationError,
                    recipient=self.config.account_number,
                    txs=txs
                )

            if len(txs) > 2:
                raise serializers.ValidationError('Only 2 Txs required when registering with confirmation validators')

        return block

    def validate_source_node_identifier(self, source_node_identifier):
        """
        Check if validator already exists
        Check for existing pending registration
        """

        if self.is_source:
            return source_node_identifier

        if Validator.objects.filter(node_identifier=source_node_identifier).exists():
            raise serializers.ValidationError('Validator with that node identifier already exists')

        if ValidatorRegistration.objects.filter(source_node_identifier=source_node_identifier, status=PENDING).exists():
            raise serializers.ValidationError(
                'Validator with that source_node_identifier already has pending registration'
            )

        return source_node_identifier

    def validate_target_node_identifier(self, target_node_identifier):
        """
        Check if validator already exists
        Check for existing pending registration
        """

        if self.is_target:
            return target_node_identifier

        if Validator.objects.filter(
            node_identifier=target_node_identifier
        ).exclude(
            self_configurations__primary_validator__node_identifier=target_node_identifier
        ).exists():
            raise serializers.ValidationError('Validator with that node identifier already exists')

        if ValidatorRegistration.objects.filter(target_node_identifier=target_node_identifier, status=PENDING).exists():
            raise serializers.ValidationError(
                'Validator with that target_node_identifier already has pending registration'
            )

        return target_node_identifier
