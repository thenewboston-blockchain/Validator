from django.urls import path

from v1.status_updates.views.primary_validator import PrimaryValidatorView

urlpatterns = [
    # Validators
    path('primary_validator_upgrade_request', PrimaryValidatorView.as_view())
]
