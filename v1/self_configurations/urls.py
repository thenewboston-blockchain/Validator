from django.urls import path

from .views.head_block_hash import head_block_hash_view
from .views.self_configuration import SelfConfigurationDetail
from .views.self_transaction_fee_tier import SelfTransactionFeeTierView

urlpatterns = [

    # Self configuration
    path('config', SelfConfigurationDetail.as_view()),

    # Head block hash
    path('head_block_hash', head_block_hash_view),

    # Self transaction fee tiers
    path('self_transaction_fee_tiers', SelfTransactionFeeTierView.as_view()),

]
