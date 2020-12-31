from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from thenewboston.constants.network import VERIFY_KEY_LENGTH

from v1.cache_tools.accounts import get_account_balance, get_account_balance_lock
from ..models.account import Account
from ..serializers.account import AccountSerializer


class AccountViewSet(
    ListModelMixin,
    GenericViewSet,
):
    """
    Accounts

    ---
    list:
      description: List accounts
    balance:
      description: Return the balance for the given account
    balance_lock:
      description: Return the balance lock for the given account
    """

    lookup_field = 'account_number'
    ordering_fields = '__all__'
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    @action(methods=['get'], detail=True)
    def balance(self, request, account_number=None):
        if account_number is not None and len(account_number) >= VERIFY_KEY_LENGTH:
            return Response({'balance': None}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({
            'balance': get_account_balance(account_number=account_number)
        })

    @action(methods=['get'], detail=True)
    def balance_lock(self, request, account_number=None):
        if  account_number is not None and len(account_number) >= VERIFY_KEY_LENGTH:
            return Response({'balance': None}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({
            'balance_lock': get_account_balance_lock(account_number=account_number)
        })
