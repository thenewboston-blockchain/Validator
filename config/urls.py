from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.index_title = 'Admin'
admin.site.site_header = 'Validator'
admin.site.site_title = 'Validator'

urlpatterns = [

    # Core
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),

    # API (v1)
    path('', include('v1.accounts.urls')),
    path('', include('v1.bank_blocks.urls')),
    path('', include('v1.bank_confirmation_services.urls')),
    path('', include('v1.banks.urls')),
    path('', include('v1.confirmation_blocks.urls')),
    path('', include('v1.connection_requests.urls')),
    path('', include('v1.meta.urls')),
    path('', include('v1.self_configurations.urls')),
    path('', include('v1.status_updates.urls')),
    path('', include('v1.validators.urls')),

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
