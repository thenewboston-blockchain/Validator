from django.urls import path

from .views.bank_confirmation_service import BankConfirmationServiceView

urlpatterns = [

    # Bank confirmation services
    path('bank_confirmation_services', BankConfirmationServiceView.as_view()),

]
