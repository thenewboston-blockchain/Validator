import json
import os
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.management.base import BaseCommand
from thenewboston.utils.fields import common_field_names
from thenewboston.utils.files import write_json

from v1.self_configurations.helpers.self_configuration import get_self_configuration
from v1.validators.models.validator import Validator

"""
python3 manage.py initialize_validator
python3 manage.py initialize_validator -h
"""


class Command(BaseCommand):
    help = 'Initialize validator as the primary validator for the network'

    def _download_json(self, *, url, file):
        """
        Download JSON file and save
        """

        try:
            request = Request(url)
            response = urlopen(request)
            results = json.loads(response.read())
            write_json(file, results)
        except Exception as e:
            self.stdout.write(self.style.ERROR(url))
            self.stdout.write(self.style.ERROR(e))

    @staticmethod
    def _update_related_validator(*, self_configuration, validator_queryset):
        """
        Update related row in the validator table
        """

        field_names = common_field_names(self_configuration, Validator)
        data = {f: getattr(self_configuration, f) for f in field_names}
        validator_queryset.update(**data)

    def handle(self, *args, **options):
        """
        Initialize validator as the primary validator for the network
        """

        self_configuration = get_self_configuration(exception_class=RuntimeError)
        validator = Validator.objects.filter(ip_address=self_configuration.ip_address)

        if not validator:
            self.stdout.write(self.style.ERROR('Could not find related validator'))
            return

        self._update_related_validator(
            self_configuration=self_configuration,
            validator_queryset=validator
        )

        self_configuration.primary_validator = validator.first()
        self_configuration.save()

        self._download_json(
            url=self_configuration.root_account_file,
            file=os.path.join(settings.TMP_DIR, 'sample2.json')
        )

        self.stdout.write(self.style.SUCCESS('ok'))
