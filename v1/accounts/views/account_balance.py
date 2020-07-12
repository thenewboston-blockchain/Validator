from rest_framework.decorators import api_view
from rest_framework.response import Response

from v1.cache_tools.accounts import get_account_balance


@api_view(['GET'])
def account_balance_view(_, account_number):
    """
    Return the balance for the given account
    """

    return Response({
        'balance': get_account_balance(account_number=account_number)
    })
