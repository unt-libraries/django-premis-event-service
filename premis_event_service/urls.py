from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^APP/$', views.app, name='app'),
    url(r'^APP/event/$', views.app_event, name='app-event'),
    url(r'^APP/event/(?P<identifier>.+?)/$', views.app_event, name='app-event-detail'),
    url(r'^APP/agent/$', views.app_agent, name='app-agent'),
    url(r'^APP/agent/(?P<identifier>.+?)/$', views.app_agent, name='app-agent-detail'),
    url(r'^event/$', views.recent_event_list, name='event-list'),
    url(r'^event/search/$', views.event_search, name='event-search'),
    url(r'^event/search.json$', views.json_event_search, name='event-search-json'),
    url(r'^event/find/(?P<linked_identifier>.+?)/(?P<event_type>.+?)?/$',
        views.findEvent, name='find-event'),
    url(r'^event/(?P<identifier>.+?)/$', views.humanEvent, name='event-detail'),
    url(r'^agent/$', views.humanAgent, name='agent-list'),
    url(r'^agent/(?P<identifier>.+?).xml$', views.agentXML, name='agent-detail-xml'),
    url(r'^agent/(?P<identifier>.+?).premis.xml$', views.agentXML, name='agent-detail-premis-xml'),
    url(r'^agent/(?P<identifier>.+?).json$', views.json_agent, name='agent-detail-json'),
    url(r'^agent/(?P<identifier>.+?)/$', views.humanAgent, name='agent-detail'),
]
