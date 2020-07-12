from rest_framework.decorators import api_view
from rest_framework.response import Response

from v1.cache_tools.accounts import get_account_balance_lock


@api_view(['GET'])
def account_balance_lock_view(_, account_number):
    """
    Return the balance lock for the given account
    """

    return Response({
        'balance_lock': get_account_balance_lock(account_number=account_number)
    })
