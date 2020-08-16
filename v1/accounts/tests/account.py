import pytest
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK
from thenewboston.third_party.pytest.asserts import assert_objects_vs_dicts


def test_accounts_list(client, accounts, django_assert_max_num_queries):
    with django_assert_max_num_queries(2):
        response = client.get_json(
            reverse('account-list'),
            {'limit': 0},
            expected=HTTP_200_OK
        )
    assert_objects_vs_dicts(accounts, response)
    assert response


def test_account_balance(client, account):
    response = client.get_json(
        reverse(
            'account-balance',
            args=[account.account_number],
        ),
        expected=HTTP_200_OK,
    )
    assert response['balance'] == pytest.approx(account.balance)


def test_account_balance_lock(client, account):
    response = client.get_json(
        reverse(
            'account-balance-lock',
            args=[account.account_number],
        ),
        expected=HTTP_200_OK,
    )
    assert response['balance_lock'] == account.balance_lock
