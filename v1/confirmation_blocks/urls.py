from django.urls import path

from .views.confirmation_block import ConfirmationBlockView
from .views.queued_confirmation_block import QueuedConfirmationBlockDetail
from .views.valid_confirmation_block import ValidConfirmationBlockDetail

urlpatterns = [

    # Confirmation blocks
    path('confirmation_blocks', ConfirmationBlockView.as_view()),

    # Queued confirmation blocks
    path('queued_confirmation_blocks/<str:block_identifier>', QueuedConfirmationBlockDetail.as_view()),

    # Valid confirmation blocks
    path('valid_confirmation_blocks/<str:block_identifier>', ValidConfirmationBlockDetail.as_view()),

]
