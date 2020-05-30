from django.core.management.base import BaseCommand

"""
python3 manage.py initialize_validator
python3 manage.py initialize_validator -h
"""


class Command(BaseCommand):
    help = 'Initialize validator as the primary validator for the network'

    def add_arguments(self, parser):
        parser.add_argument('-i', '--ip_address', metavar='', help='IP address of validator')

    def handle(self, *args, **options):
        """
        Comment here
        """

        ip_address = options['ip_address']

        if not ip_address:
            self.stdout.write(self.style.ERROR('ip_address required'))
            return

        self.stdout.write(self.style.SUCCESS(ip_address))
