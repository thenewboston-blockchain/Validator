from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from thenewboston_validator.accounts.urls import router as accounts_router
from thenewboston_validator.bank_blocks.urls import router as bank_blocks_router
from thenewboston_validator.bank_confirmation_services.urls import router as bank_confirmation_services_router
from thenewboston_validator.banks.urls import router as banks_router
from thenewboston_validator.clean.urls import router as clean_router
from thenewboston_validator.confirmation_blocks.urls import router as confirmation_blocks_router
from thenewboston_validator.crawl.urls import router as crawl_router
from thenewboston_validator.self_configurations.urls import router as self_configurations_router
from thenewboston_validator.status_updates.urls import router as status_updates_router
from thenewboston_validator.sync.urls import router as sync_router
from thenewboston_validator.validators.urls import router as validators_router

admin.site.index_title = 'Admin'
admin.site.site_header = 'Validator'
admin.site.site_title = 'Validator'

urlpatterns = [

    # Core
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),

    # API (thenewboston_validator)
    path('', include('thenewboston_validator.connection_requests.urls')),
    path('', include('thenewboston_validator.meta.urls')),
    path('', include('thenewboston_validator.self_configurations.urls')),

]

router = DefaultRouter(trailing_slash=False)

router.registry.extend(accounts_router.registry)
router.registry.extend(bank_blocks_router.registry)
router.registry.extend(bank_confirmation_services_router.registry)
router.registry.extend(banks_router.registry)
router.registry.extend(clean_router.registry)
router.registry.extend(confirmation_blocks_router.registry)
router.registry.extend(crawl_router.registry)
router.registry.extend(self_configurations_router.registry)
router.registry.extend(status_updates_router.registry)
router.registry.extend(sync_router.registry)
router.registry.extend(validators_router.registry)

urlpatterns += router.urls
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
