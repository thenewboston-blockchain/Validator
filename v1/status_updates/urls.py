from django.urls import path

from v1.status_updates.views.status_update import StatusUpdateView

urlpatterns = [
    # Validators
    path('primary_validator_upgrade_request', StatusUpdateView.as_view())
]
