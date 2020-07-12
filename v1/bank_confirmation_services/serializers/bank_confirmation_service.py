from rest_framework import serializers
from thenewboston.utils.fields import all_field_names

from ..models.bank_confirmation_service import BankConfirmationService


class BankConfirmationServiceSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = BankConfirmationService
        read_only_fields = all_field_names(BankConfirmationService)
