from django.urls import path

from v1.validator_registrations.views.validator_registration import ValidatorRegistrationView

urlpatterns = [

    # Validator registrations
    path('validator_registrations', ValidatorRegistrationView.as_view()),

]
