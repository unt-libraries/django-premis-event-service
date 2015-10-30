from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'', include('premis_event_service.urls')),
    url(r'^admin/', include(admin.site.urls)),
]
