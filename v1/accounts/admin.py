from django.contrib import admin

from .models.account import Account
from .models.transaction import Transaction

admin.site.register(Account)
admin.site.register(Transaction)
