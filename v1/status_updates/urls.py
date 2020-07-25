from django.urls import path

from .views.upgrade_request import UpgradeRequestView

urlpatterns = [

    # Upgrade request (from bank)
    path('upgrade_request', UpgradeRequestView.as_view())

]
