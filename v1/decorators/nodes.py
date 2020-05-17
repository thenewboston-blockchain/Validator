from functools import wraps

from rest_framework import status
from rest_framework.response import Response

from v1.banks.models.bank import Bank


def registered_bank(func):
    """
    Verify that the client making the request is a trusted node
    """

    @wraps(func)
    def inner(request, *args, **kwargs):
        if not request.user.is_authenticated:
            ip_address = request.META.get('REMOTE_ADDR')

            if not ip_address:
                return Response(status=status.HTTP_401_UNAUTHORIZED)

            # TODO: This should be hitting the cache
            # TODO: Proper error message formatting
            if not Bank.objects.filter(ip_address=ip_address).exists():
                return Response('Must be registered bank', status=status.HTTP_401_UNAUTHORIZED)

        return func(request, *args, **kwargs)

    return inner