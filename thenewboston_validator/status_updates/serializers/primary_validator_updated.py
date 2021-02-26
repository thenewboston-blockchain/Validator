import logging

from rest_framework import serializers
from sentry_sdk import capture_exception
from thenewboston.constants.network import (
    CONFIRMATION_VALIDATOR,
    PRIMARY_VALIDATOR,
    PROTOCOL_CHOICES,
    VERIFY_KEY_LENGTH
)
from thenewboston.utils.format import format_address
from thenewboston.utils.network import fetch

from thenewboston_validator.banks.helpers.most_trusted import get_most_trusted_bank
from thenewboston_validator.banks.models.bank import Bank
from thenewboston_validator.self_configurations.helpers.self_configuration import get_self_configuration
from thenewboston_validator.tasks.sync_with_primary_validator import sync_with_primary_validator

logger = logging.getLogger('thenewboston')


class PrimaryValidatorUpdatedSerializer(serializers.Serializer):
    ip_address = serializers.IPAddressField(protocol='both')
    node_identifier = serializers.CharField(max_length=VERIFY_KEY_LENGTH)
    port = serializers.IntegerField(allow_null=True, max_value=65535, min_value=0, required=False)
    protocol = serializers.ChoiceField(choices=PROTOCOL_CHOICES)

    def create(self, validated_data):
        """
        Handle banks primary validator updated notice

        A response of True indicates to the requesting bank that self (this validator) will remain on the same network
        Delete banks switching to different networks
        """
        bank = validated_data['node_identifier']
        ip_address = validated_data['ip_address']
        port = validated_data['port']
        protocol = validated_data['protocol']

        self_configuration = get_self_configuration(exception_class=RuntimeError)

        if self.primary_validator_synchronized(
            ip_address=ip_address,
            self_configuration=self_configuration
        ):
            return True

        if (
            self_configuration.node_type == CONFIRMATION_VALIDATOR and bank == get_most_trusted_bank()
        ):
            address = format_address(
                ip_address=ip_address,
                port=port,
                protocol=protocol
            )
            try:
                config = fetch(url=f'{address}/config', headers={})
            except Exception as e:
                capture_exception(e)
                logger.exception(e)
            else:
                sync_with_primary_validator.delay(config=config)
                return True

        bank.delete()
        raise serializers.ValidationError('Networks out of sync')

    @staticmethod
    def primary_validator_synchronized(ip_address, self_configuration):
        """Return boolean indicating if self primary validator is set to given IP address"""
        if self_configuration.node_type == CONFIRMATION_VALIDATOR:
            primary_validator = self_configuration.primary_validator

            if not primary_validator:
                return False

            if primary_validator.ip_address == ip_address:
                return True

        if self_configuration.node_type == PRIMARY_VALIDATOR:

            if self_configuration.ip_address == ip_address:
                return True

        return False

    def update(self, instance, validated_data):
        pass

    @staticmethod
    def validate_node_identifier(node_identifier):
        """Validate node_identifier is from bank"""
        bank = Bank.objects.filter(node_identifier=node_identifier).first()

        if not bank:
            raise serializers.ValidationError('Bank with that node identifier does not exists')

        return bank
