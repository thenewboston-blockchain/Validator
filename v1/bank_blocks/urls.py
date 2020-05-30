from django.urls import path

from .views.bank_block import BankBlockView

urlpatterns = [

    # Bank blocks
    path('bank_blocks', BankBlockView.as_view()),

]
