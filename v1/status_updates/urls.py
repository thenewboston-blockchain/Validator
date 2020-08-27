from rest_framework.routers import SimpleRouter

from .views.primary_validator_updated import PrimaryValidatorUpdatedViewSet
from .views.upgrade_request import UpgradeRequestViewSet

router = SimpleRouter(trailing_slash=False)
router.register('primary_validator_updated', PrimaryValidatorUpdatedViewSet, basename='primary_validator_updated')
router.register('upgrade_request', UpgradeRequestViewSet, basename='upgrade_request')
