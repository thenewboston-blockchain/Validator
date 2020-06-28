from v1.self_configurations.management.commands.initialize_test_validator import Command
from .test_base import TestBase


class TestPrimaryValidator(TestBase):

    def setUp(self):
        """
        Initialize test primary validator
        """

        Command().handle(ip='127.0.0.1')
