from django.urls import path

from .views.head_block_hash import HeadBlockHashDetail
from .views.self_configuration import SelfConfigurationDetail
from .views.self_transaction_fee_tier import SelfTransactionFeeTierView

urlpatterns = [

    # Self configuration
    path('config', SelfConfigurationDetail.as_view()),

    # Head block hash
    path('head_block_hash', HeadBlockHashDetail.as_view()),

    # Self transaction fee tiers
    path('self_transaction_fee_tiers', SelfTransactionFeeTierView.as_view()),

]
