from django.core.urlresolvers import resolve

from premis_event_service import views


def test_app():
    url = resolve('/APP/')
    assert url.func == views.app


def test_app_event_without_identifier():
    url = resolve('/APP/event/')
    assert url.func == views.app_event


def test_app_event_with_identifier():
    url = resolve('/APP/event/00000000000000000000000000000000/')
    assert url.func == views.app_event


def test_app_agent_without_identifier():
    url = resolve('/APP/agent/')
    assert url.func == views.app_agent


def test_app_agent_with_identifier():
    url = resolve('/APP/agent/agentId/')
    assert url.func == views.app_agent


def test_event_list():
    url = resolve('/event/')
    assert url.func == views.recent_event_list


def test_event_search():
    url = resolve('/event/search/')
    assert url.func == views.event_search


def test_event_search_json():
    url = resolve('/event/search.json')
    assert url.func == views.json_event_search


def test_findEvent():
    url = resolve('/event/find/ark:/00001/coda1n/00000000000000000000000000000000/')
    assert url.func == views.findEvent


def test_humanEvent():
    url = resolve('/event/00000000000000000000000000000000/')
    assert url.func == views.humanEvent


def test_humanAgent_without_identifier():
    url = resolve('/agent/')
    assert url.func == views.humanAgent


def test_humanAgent_with_identifier():
    url = resolve('/agent/agentId/')
    assert url.func == views.humanAgent


def test_agentXML():
    url = resolve('/agent/agentId.xml')
    assert url.func == views.agentXML


def test_premis_agentXML():
    url = resolve('/agent/agentId.premis.xml')
    assert url.func == views.agentXML


def test_json_agent():
    url = resolve('/agent/agentId.json')
    assert url.func == views.json_agent
