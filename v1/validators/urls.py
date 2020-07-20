from django.urls import path

from .views.validator import ValidatorView
from .views.primary_validator import PrimaryValidatorView

urlpatterns = [

    # Validators
    path('validators', ValidatorView.as_view()),
    path('primary_validator_upgrade_request', PrimaryValidatorView.as_view())
]
