import os

from django.contrib.auth import get_user_model
from django.core import management
from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.core.management.commands import loaddata
from django.core.validators import validate_ipv46_address

from config.helpers.environment import ENVIRONMENT
from v1.accounts.models.account import Account
from v1.banks.models.bank import Bank
from v1.constants.cache_keys import (
    BANK_BLOCK_QUEUE,
    CONFIRMATION_BLOCK_QUEUE,
    HEAD_HASH,
    get_account_balance_cache_key,
    get_account_balance_lock_cache_key
)
from v1.self_configurations.helpers.self_configuration import get_self_configuration
from v1.self_configurations.models.self_configuration import SelfConfiguration
from v1.validators.models.validator import Validator

"""
python3 manage.py initialize_local_validator

Running this script will:
- delete all Accounts, Banks, SelfConfigurations, Users, and Validators
- load in fixture data (same models as above)
- rebuild cache

Fixture data sets self as the primary validator.

Default superuser is:
username: bucky
password: pass1234
"""

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(CURRENT_DIR, 'fixtures')

User = get_user_model()


class Command(BaseCommand):
    help = 'Delete existing data, load in fixture data, set self as primary validator, rebuild cache'

    def add_arguments(self, parser):
        """
        Required arguments:
        -ip_address - Public IP address
        """

        parser.add_argument('-ip', help='Public IP address', required=True)

    def handle(self, *args, **options):
        """
        Run script
        """

        valid_environments = ['local', 'postgres_local']

        if ENVIRONMENT not in valid_environments:
            raise RuntimeError(f'DJANGO_APPLICATION_ENVIRONMENT must be in {valid_environments}')

        ip = options['ip']
        validate_ipv46_address(ip)

        self.install_fixture_data()

        self_configuration = get_self_configuration(exception_class=RuntimeError)
        SelfConfiguration.objects.filter(pk=self_configuration.id).update(ip_address=ip)
        validator = self_configuration.primary_validator
        validator.ip_address = ip
        validator.save()

        self.rebuild_cache(head_hash=self_configuration.head_hash)
        self.stdout.write(self.style.SUCCESS('Validator initialization complete'))

    def install_fixture_data(self):
        """
        Delete all Accounts, Banks, SelfConfigurations, Users, and Validators
        Load in fixture data (same models as above)
        """

        global FIXTURES_DIR

        self.stdout.write(self.style.SUCCESS('Installing fixture data...'))

        Account.objects.all().delete()
        Bank.objects.all().delete()
        SelfConfiguration.objects.all().delete()
        User.objects.all().delete()
        Validator.objects.all().delete()

        fixture_files = [
            'validator.json',
            'account.json',
            'bank.json',
            'self_configuration.json',
            'user.json'
        ]

        for fixture_file in fixture_files:
            fixtures = os.path.join(FIXTURES_DIR, fixture_file)
            management.call_command(loaddata.Command(), fixtures, verbosity=1)

        self.stdout.write(self.style.SUCCESS('Fixture data installed successfully'))

    def rebuild_cache(self, *, head_hash):
        """
        Rebuild cache
        """

        self.stdout.write(self.style.SUCCESS('Rebuilding cache...'))

        cache.clear()
        cache.set(BANK_BLOCK_QUEUE, [], None)
        cache.set(CONFIRMATION_BLOCK_QUEUE, [], None)
        cache.set(HEAD_HASH, head_hash, None)

        accounts = Account.objects.all()

        for account in accounts:
            account_number = account.account_number
            account_balance_cache_key = get_account_balance_cache_key(account_number=account_number)
            account_balance_lock_cache_key = get_account_balance_lock_cache_key(account_number=account_number)
            cache.set(account_balance_cache_key, account.balance, None)
            cache.set(account_balance_lock_cache_key, account.balance_lock, None)

        self.stdout.write(self.style.SUCCESS('Cache rebuilt successfully'))
