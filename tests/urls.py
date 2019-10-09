import os

from django.conf.urls import include, url
from . import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'', include('premis_event_service.urls')),
    url(r'^admin/', admin.site.urls),
]

if settings.DEBUG and os.getenv('PES_DEBUG_TOOLBAR'):
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
