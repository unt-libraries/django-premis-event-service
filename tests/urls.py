import os

from django.conf.urls import include, url
from . import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url('', include('premis_event_service.urls')),
    url('admin/', admin.site.urls),
]

if settings.DEBUG and os.getenv('PES_DEBUG_TOOLBAR'):
    import debug_toolbar
    urlpatterns += [
        url('__debug__/', include(debug_toolbar.urls)),
    ]
