from django.urls import path

from .views.account import AccountView
from .views.account_balance_lock import account_balance_lock_view

urlpatterns = [

    # Accounts
    path('accounts', AccountView.as_view()),

    # Account balance lock
    path('account_balance_lock/<str:account_number>', account_balance_lock_view),

]
