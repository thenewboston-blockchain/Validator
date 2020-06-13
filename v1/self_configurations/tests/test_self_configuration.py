from rest_framework import status
from thenewboston.constants.network import VALIDATOR

from v1.test_tools.test_base import TestBase


class TestSelfConfiguration(TestBase):

    def test_get(self):
        """
        Get self configuration details
        """

        response = self.validate_get('/config', status.HTTP_200_OK)
        config = response.json()

        primary_validator = config['primary_validator']
        node_type = config['node_type']

        self.assertIsInstance(primary_validator, dict)
        self.assertEqual(node_type, VALIDATOR)