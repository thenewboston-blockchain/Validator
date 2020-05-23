from django.urls import path

from .views.account import AccountView
from .views.transaction import TransactionView

urlpatterns = [

    # Accounts
    path('accounts', AccountView.as_view()),

    # Transactions
    path('transactions', TransactionView.as_view()),

]
