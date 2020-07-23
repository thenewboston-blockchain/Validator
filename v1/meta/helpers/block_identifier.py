from django.core.cache import cache
from thenewboston.utils.messages import get_message_hash

from v1.cache_tools.cache_keys import get_confirmation_block_cache_key
from v1.self_configurations.helpers.self_configuration import get_self_configuration


def get_initial_block_identifier():
    """
    Return initial block identifier

    If seed_block_identifier, fetch related (seed) block and hash to get initial block identifier
    Otherwise, return root_account_file_hash
    """

    self_configuration = get_self_configuration(exception_class=RuntimeError)
    seed_block_identifier = self_configuration.seed_block_identifier

    if seed_block_identifier:
        confirmation_block_cache_key = get_confirmation_block_cache_key(block_identifier=seed_block_identifier)
        confirmation_block = cache.get(confirmation_block_cache_key)
        return get_message_hash(message=confirmation_block['message'])

    return self_configuration.root_account_file_hash
