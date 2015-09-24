import json

import pytest

from django.http import Http404
from django.core.urlresolvers import reverse

from premis_event_service import views
from . import factories


pytestmark = pytest.mark.urls('premis_event_service.urls')


def test_app_returns_ok(rf):
    request = rf.get('/')
    response = views.app(request)
    assert response.status_code == 200


def test_app_content_type(rf):
    request = rf.get('/')
    response = views.app(request)
    assert response.get('Content-Type') == 'application/atom+xml'


@pytest.mark.xfail
def test_app_content(rf):
    assert 0


@pytest.mark.django_db
def test_humanEvent_raises_http404(rf):
    request = rf.get('/')
    with pytest.raises(Http404):
        views.humanEvent(request)


@pytest.mark.django_db
def test_humanEvent_returns_ok(rf):
    event = factories.EventFactory.create()
    request = rf.get('/')
    response = views.humanEvent(request, event.event_identifier)
    assert response.status_code == 200


@pytest.mark.django_db
def test_json_event_list_returns_ok(rf):
    factories.EventFactory.create_batch(30)
    request = rf.get('/')
    response = views.recent_event_list(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_json_event_list_context(client):
    num_events = 30
    factories.EventFactory.create_batch(num_events)
    response = client.get(reverse('premis_event_service.views.recent_event_list'))

    context = response.context[-1]
    assert len(context['entries']) == 10
    assert context['num_events'] == num_events


@pytest.mark.django_db
def test_json_event_list_with_no_events(rf):
    request = rf.get('/')
    response = views.recent_event_list(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_json_agent_returns_ok(rf):
    agent = factories.AgentFactory.create()
    request = rf.get('/')
    response = views.json_agent(request, agent.agent_identifier)
    assert response.status_code == 200
    assert response.get('Content-Type') == 'application/json'


@pytest.mark.django_db
def test_json_agent_payload(rf):
    agent = factories.AgentFactory.create()
    request = rf.get('/')
    response = views.json_agent(request, agent.agent_identifier)
    payload = json.loads(response.content)

    assert agent.get_absolute_url() in payload['id']
    assert payload['type'] == agent.agent_type
    assert payload['name'] == agent.agent_name
    assert payload['note'] == agent.agent_note


@pytest.mark.django_db
def test_agent_xml_returns_ok(rf):
    agent = factories.AgentFactory.create()
    request = rf.get('/')
    response = views.agentXML(request, agent.agent_identifier)
    assert response.status_code == 200


@pytest.mark.django_db
def test_agent_xml_returns_not_found(rf):
    identifier = 'ark:/00001/dne'
    request = rf.get('/')
    response = views.agentXML(request, identifier)
    assert response.status_code == 404


@pytest.mark.django_db
def test_agent_xml_content_type(rf):
    agent = factories.AgentFactory.create()
    request = rf.get('/')
    response = views.agentXML(request, agent.agent_identifier)
    assert response.get('Content-Type') == 'application/atom+xml'


@pytest.mark.django_db
def test_agent_xml_returns_ok_with_premis_identifier(rf):
    # Create an agent and update the identifier to include `.premis`.
    agent = factories.AgentFactory.create()
    agent.identifier = 'ark:/00001/coda1n.premis'
    agent.save()

    request = rf.get('/.premis')
    response = views.agentXML(request, agent.agent_identifier)

    assert response.status_code == 200


@pytest.mark.django_db
def test_agent_xml_returns_not_found_with_premis_identifier(rf):
    identifier = 'ark:/00001/coda1n.premis'
    request = rf.get('/.premis')
    response = views.agentXML(request, identifier)
    assert response.status_code == 404
