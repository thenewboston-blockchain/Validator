from rest_framework.routers import SimpleRouter

from .views.bank_block import BankBlockViewSet

router = SimpleRouter(trailing_slash=False)
router.register('bank_blocks', BankBlockViewSet, basename='bank_blocks')
