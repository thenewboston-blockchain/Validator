import logging
from functools import wraps

from nacl.exceptions import BadSignatureError
from rest_framework import status
from rest_framework.response import Response
from thenewboston.blocks.signatures import verify_signature
from thenewboston.constants.errors import BAD_SIGNATURE, ERROR, UNKNOWN
from thenewboston.utils.tools import sort_and_encode

from v1.banks.models.bank import Bank

logger = logging.getLogger('thenewboston')


def verify_request_signature(*, request, signed_data_key):
    """
    Verify the request signature

    signed_data - block or message
    """

    node_identifier = request.data.get('node_identifier')
    signature = request.data.get('signature')
    signed_data = request.data.get(signed_data_key)

    for field in ['node_identifier', 'signature', signed_data_key]:
        if not request.data.get(field):
            return request, {ERROR: f'{field} required'}

    error = None

    try:
        verify_signature(
            message=sort_and_encode(signed_data),
            signature=signature,
            verify_key=node_identifier
        )
    except BadSignatureError as e:
        logger.exception(e)
        error = {ERROR: BAD_SIGNATURE}
    except Exception as e:
        logger.exception(e)
        error = {ERROR: UNKNOWN}

    return request, error


def is_signed_bank_block(func):
    """
    Decorator to verify:
    - block data exists
    - block signature
    - signer is registered bank
    """

    @wraps(func)
    def inner(request, *args, **kwargs):
        request, error = verify_request_signature(request=request, signed_data_key='block')

        if error:
            return Response(error, status=status.HTTP_401_UNAUTHORIZED)

        node_identifier = request.data.get('node_identifier')

        # TODO: This should be hitting the cache
        if not Bank.objects.filter(node_identifier=node_identifier).exists():
            return Response(
                {ERROR: f'Bank with node_identifier {node_identifier} not registered'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        return func(request, *args, **kwargs)

    return inner


def is_signed_message(func):
    """
    Decorator to verify the request signature
    """

    @wraps(func)
    def inner(request, *args, **kwargs):
        request, error = verify_request_signature(request=request, signed_data_key='message')

        if error:
            return Response(error, status=status.HTTP_401_UNAUTHORIZED)

        return func(request, *args, **kwargs)

    return inner
