import pytest

from ..factories.account import AccountFactory


@pytest.fixture
def account():
    yield AccountFactory()


@pytest.fixture
def accounts():
    yield AccountFactory.create_batch(100)
