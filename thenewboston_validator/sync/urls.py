from rest_framework.routers import SimpleRouter

from .views.confirmation_block_history import ConfirmationBlockHistoryViewSet

router = SimpleRouter(trailing_slash=False)
router.register('confirmation_block_history', ConfirmationBlockHistoryViewSet, basename='confirmation_block_history')
