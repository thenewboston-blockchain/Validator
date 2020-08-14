from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from v1.accounts.urls import router as accounts_router
from v1.bank_confirmation_services.urls import router as bank_confirmation_services_router
from v1.banks.urls import router as banks_router
from v1.self_configurations.urls import router as self_configurations_router
from v1.validators.urls import router as validators_router

admin.site.index_title = 'Admin'
admin.site.site_header = 'Validator'
admin.site.site_title = 'Validator'

urlpatterns = [

    # Core
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),

    # API (v1)
    path('', include('v1.bank_blocks.urls')),
    path('', include('v1.confirmation_blocks.urls')),
    path('', include('v1.connection_requests.urls')),
    path('', include('v1.meta.urls')),
    path('', include('v1.self_configurations.urls')),
    path('', include('v1.status_updates.urls')),

]

router = DefaultRouter(trailing_slash=False)

router.registry.extend(accounts_router.registry)
router.registry.extend(bank_confirmation_services_router.registry)
router.registry.extend(banks_router.registry)
router.registry.extend(self_configurations_router.registry)
router.registry.extend(validators_router.registry)

urlpatterns += router.urls
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
