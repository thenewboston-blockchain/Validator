from django.urls import path

from .views.bank_registration import BankRegistrationView

urlpatterns = [

    # Bank registrations
    path('bank_registrations', BankRegistrationView.as_view()),

]
