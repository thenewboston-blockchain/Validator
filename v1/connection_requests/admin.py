from django.contrib import admin

from .models.connection_request import ConnectionRequest

admin.site.register(ConnectionRequest)
