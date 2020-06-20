from functools import wraps

from nacl.exceptions import BadSignatureError
from rest_framework import status
from rest_framework.response import Response
from thenewboston.blocks.signatures import verify_signature
from thenewboston.utils.tools import sort_and_encode

from v1.banks.models.bank import Bank


def is_registered_bank(func):
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
            if not Bank.objects.filter(ip_address=ip_address).exists():
                return Response(status=status.HTTP_401_UNAUTHORIZED)

        return func(request, *args, **kwargs)

    return inner


def is_signed_request(func):
    """
    Verify the request signature
    """

    @wraps(func)
    def inner(request, *args, **kwargs):
        message = request.data.get('message')
        network_identifier = request.data.get('network_identifier')
        signature = request.data.get('signature')

        try:
            verify_signature(
                message=sort_and_encode(message),
                signature=signature,
                verify_key=network_identifier
            )
        except BadSignatureError:
            # TODO: Standardize error messages
            return Response(
                {'Error': 'Bad signature'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            # TODO: Standardize error messages
            print(e)
            return Response(
                {'Error': 'Unknown error'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        return func(request, *args, **kwargs)

    return inner
