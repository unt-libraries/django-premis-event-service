import os

from django.urls import path, include
from . import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    path('', include('premis_event_service.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG and os.getenv('PES_DEBUG_TOOLBAR'):
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
