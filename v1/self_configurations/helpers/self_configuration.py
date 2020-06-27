from ..models.self_configuration import SelfConfiguration


def get_primary_validator():
    """
    Return primary validator
    """

    # TODO: This should be hitting the cache

    self_configuration = get_self_configuration(exception_class=RuntimeError)
    return self_configuration.primary_validator


def get_self_configuration(*, exception_class):
    """
    Return self configuration
    """

    self_configuration = SelfConfiguration.objects.first()

    if not self_configuration:
        raise exception_class('No self configuration')

    return self_configuration
