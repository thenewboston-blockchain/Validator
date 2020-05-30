from hashlib import sha3_256 as sha3

from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.cache import cache
from nacl.encoding import HexEncoder
from nacl.signing import SigningKey
from thenewboston.blocks.signatures import generate_signature
from thenewboston.environment.environment_variables import get_environment_variable
from thenewboston.utils.format import format_address
from thenewboston.utils.network import post
from thenewboston.utils.tools import sort_and_encode
from thenewboston.verify_keys.verify_key import encode_verify_key, get_verify_key

from v1.accounts.models.account import Account
from v1.constants.cache_keys import HEAD_HASH, get_account_balance_cache_key, get_account_balance_lock_cache_key

logger = get_task_logger(__name__)


def get_message_hash(*, message):
    """
    Generate a balance lock from a Tx
    """

    return sha3(sort_and_encode(message)).digest().hex()


def update_accounts_table(*, sender_account_number, recipient_account_numbers):
    """
    Update the accounts table in the database
    Return updated balances
    """

    results = []

    sender_account_balance_cache_key = get_account_balance_cache_key(account_number=sender_account_number)
    sender_account_balance_lock_cache_key = get_account_balance_lock_cache_key(account_number=sender_account_number)
    sender_account_balance = cache.get(sender_account_balance_cache_key)
    sender_account_balance_lock = cache.get(sender_account_balance_lock_cache_key)

    Account.objects.filter(account_number=sender_account_number).update(
        balance=sender_account_balance,
        balance_lock=sender_account_balance_lock
    )

    results.append({
        'account_number': sender_account_number,
        'balance': str(sender_account_balance),
        'balance_lock': sender_account_balance_lock
    })

    for recipient in recipient_account_numbers:
        recipient_account_balance_cache_key = get_account_balance_cache_key(account_number=recipient)
        recipient_account_balance = cache.get(recipient_account_balance_cache_key)
        Account.objects.filter(account_number=recipient).update(balance=recipient_account_balance)

        results.append({
            'account_number': recipient,
            'balance': str(recipient_account_balance)
        })

    return results


@shared_task
def sign_and_send_confirmed_block(*, block, ip_address, new_balance_lock, port, protocol, url_path):
    """
    Sign block and send to recipient
    """

    head_hash = cache.get(HEAD_HASH)
    network_signing_key = get_environment_variable('NETWORK_SIGNING_KEY')
    signing_key = SigningKey(network_signing_key, encoder=HexEncoder)
    network_identifier = get_verify_key(signing_key=signing_key)
    network_identifier = encode_verify_key(verify_key=network_identifier)

    sender_account_number = block['account_number']
    sender_account_balance_cache_key = get_account_balance_cache_key(account_number=sender_account_number)
    sender_account_balance_lock_cache_key = get_account_balance_lock_cache_key(account_number=sender_account_number)
    sender_account_balance = cache.get(sender_account_balance_cache_key)

    txs = block['txs']
    total_amount = sum([tx['amount'] for tx in txs])

    # Update sender account
    cache.set(sender_account_balance_cache_key, sender_account_balance - total_amount)
    cache.set(sender_account_balance_lock_cache_key, new_balance_lock)

    # Update recipient accounts
    for tx in txs:
        amount = tx['amount']
        recipient = tx['recipient']
        recipient_account_balance_cache_key = get_account_balance_cache_key(account_number=recipient)
        recipient_account_balance = cache.get(recipient_account_balance_cache_key)

        if recipient_account_balance is None:
            cache.set(recipient_account_balance_cache_key, amount)
        else:
            cache.set(recipient_account_balance_cache_key, recipient_account_balance + amount)

    updated_balances = update_accounts_table(
        sender_account_number=sender_account_number,
        recipient_account_numbers=[tx['recipient'] for tx in txs]
    )

    message = {
        'block': block,
        'block_identifier': head_hash,
        'updated_balances': updated_balances
    }
    confirmed_block = {
        'message': message,
        'network_identifier': network_identifier,
        'signature': generate_signature(message=sort_and_encode(message), signing_key=signing_key)
    }

    message_hash = get_message_hash(message=message)
    cache.set(HEAD_HASH, message_hash, None)

    node_address = format_address(ip_address=ip_address, port=port, protocol=protocol)
    url = f'{node_address}{url_path}'

    try:
        post(url=url, body=confirmed_block)
    except Exception as e:
        # TODO: Log these and consider reducing the trust of the offending bank
        logger.error(e)
