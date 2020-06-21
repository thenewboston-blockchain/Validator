import logging
from functools import wraps

from nacl.exceptions import BadSignatureError
from rest_framework import status
from rest_framework.response import Response
from thenewboston.blocks.signatures import verify_signature
from thenewboston.utils.tools import sort_and_encode

from v1.banks.models.bank import Bank

logger = logging.getLogger('thenewboston')


def verify_request_signature(request):
    """
    Verify the request signature
    """

    message = request.data.get('message')
    network_identifier = request.data.get('network_identifier')
    signature = request.data.get('signature')

    for field in ['message', 'network_identifier', 'signature']:
        if not request.data.get(field):
            return request, {'Error': f'{field} required'}

    error = None

    try:
        verify_signature(
            message=sort_and_encode(message),
            signature=signature,
            verify_key=network_identifier
        )
    except BadSignatureError as e:
        logger.exception(e)
        # TODO: Standardize error messages
        error = {'Error': 'Bad signature'}
    except Exception as e:
        logger.exception(e)
        # TODO: Standardize error messages
        error = {'Error': 'Unknown error'}

    return request, error


def is_registered_bank(func):
    """
    Decorator to verify that the client making the request is a trusted node
    """

    @wraps(func)
    def inner(request, *args, **kwargs):
        request, error = verify_request_signature(request)

        if error:
            return Response(error, status=status.HTTP_401_UNAUTHORIZED)

        network_identifier = request.data.get('network_identifier')

        # TODO: This should be hitting the cache
        if not Bank.objects.filter(network_identifier=network_identifier).exists():
            return Response(
                {'Error': f'Bank with network_identifier {network_identifier} not registered'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        return func(request, *args, **kwargs)

    return inner


def is_signed_request(func):
    """
    Decorator to verify the request signature
    """

    @wraps(func)
    def inner(request, *args, **kwargs):
        request, error = verify_request_signature(request)

        if error:
            return Response(error, status=status.HTTP_401_UNAUTHORIZED)

        return func(request, *args, **kwargs)

    return inner
