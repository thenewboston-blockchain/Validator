import json
from urllib.request import Request, urlopen

from django.conf import settings
from thenewboston.utils.files import read_json, write_json

from thenewboston_validator.accounts.models.account import Account


def download_root_account_file(*, url):
    """Download root account JSON file and save"""
    request = Request(url)
    response = urlopen(request)

    results = json.loads(response.read())
    write_json(settings.ROOT_ACCOUNT_FILE_PATH, results)


def sync_accounts_table_to_root_account_file():
    """Sync Account objects using root account file data"""
    Account.objects.all().delete()
    account_data = read_json(settings.ROOT_ACCOUNT_FILE_PATH)
    accounts = [
        Account(
            account_number=k,
            balance=v['balance'],
            balance_lock=v['balance_lock']
        ) for k, v in account_data.items()
    ]
    Account.objects.bulk_create(accounts)
