from django.conf.urls.defaults import *

urlpatterns = patterns(
    'premis_event_service.views',
    # begin CODA Family url structure >
    (r'^APP/$', 'app'),
    # node urls
    # (r'^APP/node/$', 'node'),
    # (r'^APP/node/(?P<identifier>.+?)/$', 'node'),
    # event urls
    (r'^APP/event/$', 'app_event'),
    (r'^APP/event/(?P<identifier>.+?)/$', 'app_event'),
    # agent urls
    (r'^APP/agent/$', 'app_agent'),
    (r'^APP/agent/(?P<identifier>.+?)/$', 'app_agent'),
    # html view urls
    (r'^event/$', 'recent_event_list'),
    (r'^event/search/$', 'event_search'),
    (r'^event/search.json$', 'json_event_search'),
    (r'^event/find/(?P<linked_identifier>.+?)/(?P<event_type>.+?)?/$', 'findEvent'),
    (r'^event/(?P<identifier>.+?)/$', 'humanEvent'),
    (r'^agent/$', 'humanAgent'),
    (r'^agent/(?P<identifier>.+?).xml$', 'agentXML'),
    (r'^agent/(?P<identifier>.+?).premis.xml$', 'agentXML'),
    (r'^agent/(?P<identifier>.+?).json$', 'json_agent'),
    (r'^agent/(?P<identifier>.+?)/$', 'humanAgent'),
)
