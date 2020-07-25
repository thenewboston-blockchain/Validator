import logging

from celery import shared_task
from thenewboston.utils.format import format_address
from thenewboston.utils.network import patch, post
from thenewboston.utils.signed_requests import generate_signed_request

from v1.self_configurations.helpers.signing_key import get_signing_key

logger = logging.getLogger('thenewboston')


@shared_task
def send_signed_patch_request(*, data, ip_address, port, protocol, url_path):
    """
    Sign data and send to recipient
    """

    signed_request = generate_signed_request(
        data=data,
        nid_signing_key=get_signing_key()
    )

    node_address = format_address(ip_address=ip_address, port=port, protocol=protocol)
    url = f'{node_address}{url_path}'

    try:
        patch(url=url, body=signed_request)
    except Exception as e:
        logger.exception(e)


@shared_task
def send_signed_post_request(*, data, ip_address, port, protocol, url_path):
    """
    Sign data and send to recipient
    """

    signed_request = generate_signed_request(
        data=data,
        nid_signing_key=get_signing_key()
    )

    node_address = format_address(ip_address=ip_address, port=port, protocol=protocol)
    url = f'{node_address}{url_path}'

    try:
        post(url=url, body=signed_request)
    except Exception as e:
        logger.exception(e)
