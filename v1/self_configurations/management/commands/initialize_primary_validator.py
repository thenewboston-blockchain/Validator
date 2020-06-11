from django.core.management.base import BaseCommand, CommandError

from v1.self_configurations.models.self_configuration import SelfConfiguration
from v1.validators.models.validator import Validator

"""
python3 manage.py initialize_primary_validator
"""


class Command(BaseCommand):
    help = 'Initialize primary validator'

    @staticmethod
    def check_initialization_requirements():
        """
        Verify that no existing SelfConfiguration or Validator(s) already exist
        """

        if SelfConfiguration.objects.exists():
            raise CommandError('Unable to initialize with existing SelfConfiguration')

        if Validator.objects.exists():
            raise CommandError('Unable to initialize with existing Validator(s)')

    def handle(self, *args, **options):
        """
        Run script
        """

        print(options)
        self.check_initialization_requirements()
        self.stdout.write(self.style.SUCCESS('Nice'))
