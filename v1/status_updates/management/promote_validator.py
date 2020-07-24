from v1.self_configurations.helpers.self_configuration import get_self_configuration
from v1.self_configurations.models.self_configuration import SelfConfiguration
from v1.validators.models.validator import Validator


def promote_confirmation_validator():
    """
    This method promotes the current confirmation validator to
    a primary validator
    """
    self_configuration: SelfConfiguration = get_self_configuration(exception_class=RuntimeError)
    validator = Validator.objects.filter(node_identifier=self_configuration.node_identifier).first()

    if validator is None:
        raise RuntimeError(f"validator {self_configuration.node_identifier} not registered")

    self_configuration.update(primary_validator=validator)
