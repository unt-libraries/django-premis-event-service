from django.urls import path
from . import views

urlpatterns = [
    path('APP/', views.app, name='app'),
    path('APP/event/', views.app_event, name='app-event'),
    path('APP/event/<identifier>/', views.app_event, name='app-event-detail'),
    path('APP/agent/', views.app_agent, name='app-agent'),
    path('APP/agent/<identifier>/', views.app_agent, name='app-agent-detail'),
    path('event/', views.recent_event_list, name='event-list'),
    path('event/search/', views.event_search, name='event-search'),
    path('event/search.json', views.json_event_search, name='event-search-json'),
#    path('event/find/<linked_identifier>/<event_type>/',
    path('event/find/(?P<linked_identifier>.+?)/(?P<event_type>.+?)?/$',
         views.findEvent, name='find-event'),
    path('event/<identifier>/', views.humanEvent, name='event-detail'),
    path('agent/', views.humanAgent, name='agent-list'),
    path('agent/<identifier>.xml', views.agentXML, name='agent-detail-xml'),
    path('agent/<identifier>.premis.xml', views.agentXML, name='agent-detail-premis-xml'),
    path('agent/<identifier>.json', views.json_agent, name='agent-detail-json'),
    path('agent/<identifier>/', views.humanAgent, name='agent-detail'),
]
