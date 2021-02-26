from thenewboston_validator.self_configurations.helpers.self_configuration import get_self_configuration


def get_initial_block_identifier():
    """Return initial block identifier (seed_block_identifier or root_account_file_hash)"""
    self_configuration = get_self_configuration(exception_class=RuntimeError)
    return self_configuration.seed_block_identifier or self_configuration.root_account_file_hash
