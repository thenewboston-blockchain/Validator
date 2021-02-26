from rest_framework.routers import SimpleRouter

from .views.bank_confirmation_service import BankConfirmationServiceViewSet

router = SimpleRouter(trailing_slash=False)
router.register('bank_confirmation_services', BankConfirmationServiceViewSet)
