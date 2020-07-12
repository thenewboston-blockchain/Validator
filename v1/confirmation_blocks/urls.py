from django.urls import path

from .views.confirmation_block import ConfirmationBlockDetail, ConfirmationBlockView
from .views.confirmation_block_chain_segment import ConfirmationBlockChainSegmentView

urlpatterns = [

    # Confirmation blocks
    path('confirmation_blocks', ConfirmationBlockView.as_view()),
    path('confirmation_blocks/<str:block_identifier>', ConfirmationBlockDetail.as_view()),

    # Confirmation block chain segment
    path('confirmation_block_chain_segment/<str:block_identifier>', ConfirmationBlockChainSegmentView.as_view()),

]
