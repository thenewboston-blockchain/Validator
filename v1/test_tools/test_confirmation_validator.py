from v1.self_configurations.management.commands.initialize_test_confirmation_validator import Command
from .test_base import TestBase


class TestConfirmationValidator(TestBase):

    def setUp(self):
        """
        Initialize test confirmation validator
        """

        Command().handle(ip='127.0.0.1')
