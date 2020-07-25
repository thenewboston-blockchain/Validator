from django.urls import path

from .views.primary_validator_updated import PrimaryValidatorUpdatedView
from .views.upgrade_request import UpgradeRequestView

urlpatterns = [

    # Primary validator updated (from bank)
    path('primary_validator_updated', PrimaryValidatorUpdatedView.as_view()),

    # Upgrade request (from bank)
    path('upgrade_request', UpgradeRequestView.as_view())

]
