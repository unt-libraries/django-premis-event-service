import json

import pytest

from django.http import Http404
from django.core.urlresolvers import reverse

from premis_event_service import views, models
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


def test_eventXML(rf):
    request = rf.get('/')
    response = views.eventXML(request)
    assert response.status_code == 200
    assert "So you would like XML for the event with identifier" in response.content


@pytest.mark.django_db
def test_find_event_returns_ok(rf):
    event = factories.EventFactory.create(linking_objects=True)
    request = rf.get('/')
    linking_object = event.linking_objects.first()
    response = views.findEvent(request, linking_object.object_identifier)
    assert response.status_code == 200


@pytest.mark.django_db
def test_find_event_response_content_type(rf):
    event = factories.EventFactory.create(linking_objects=True)
    request = rf.get('/')
    linking_object = event.linking_objects.first()
    response = views.findEvent(request, linking_object.object_identifier)

    assert response.get('Content-Type') == 'application/atom+xml'


@pytest.mark.django_db
def test_find_event_returns_not_found(rf):
    request = rf.get('/')
    response = views.findEvent(request, 'fake-identifier')
    assert response.status_code == 404


@pytest.mark.django_db
def test_find_event_finds_multiple_events(rf):
    # Create two events.
    event1 = factories.EventFactory.create(linking_objects=True)
    event2 = factories.EventFactory.create()

    # Get one of the related LinkObjects from event1 and add it to event2.
    linking_object = event1.linking_objects.first()
    event2.linking_objects.add(linking_object)
    event2.save()

    request = rf.get('/')
    response = views.findEvent(request, linking_object.object_identifier)

    # Determine which event is the oldest.
    new_event, old_event = sorted([event1, event2], key=lambda e: e.event_date_time)

    # Check that only the oldest event is present in the xml content.
    assert old_event.event_identifier in response.content
    assert new_event.event_identifier not in response.content


@pytest.mark.django_db
def test_app_agent_get_without_identifier_returns_ok(rf):
    request = rf.get('/')
    response = views.app_agent(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_app_agent_get_without_identifier_content_type(rf):
    request = rf.get('/')
    response = views.app_agent(request)
    assert response.get('Content-Type') == 'application/atom+xml'


@pytest.mark.xfail(reason='EmptyPage exception is not handled.')
@pytest.mark.django_db
def test_app_agent_get_with_invalid_page_without_identifier(rf):
    request = rf.get('/?page=3')
    views.app_agent(request)


@pytest.fixture
def app_agent_xml():
    xml = """<?xml version="1.0"?>
        <premis:agent xmlns:premis="info:lc/xmlns/premis-v2">
          <premis:agentIdentifier>
            <premis:agentIdentifierValue>{identifier}</premis:agentIdentifierValue>
            <premis:agentIdentifierType>PES:Agent</premis:agentIdentifierType>
          </premis:agentIdentifier>
          <premis:agentName>asXbNNQgsgbS</premis:agentName>
          <premis:agentType>Software</premis:agentType>
        </premis:agent>
    """
    identifier = 'EqLVtAeVnHoR'
    return identifier, xml.format(identifier=identifier)


@pytest.mark.django_db
def test_app_agent_post_without_identifier_returns_created(rf, app_agent_xml):
    _, xml = app_agent_xml
    request = rf.post('/', xml, content_type='application/xml')
    response = views.app_agent(request)
    assert response.status_code == 201


@pytest.mark.django_db
def test_app_agent_post_without_identifier_content_type(rf, app_agent_xml):
    _, xml = app_agent_xml
    request = rf.post('/', xml, content_type='application/xml')
    response = views.app_agent(request)
    assert response.get('Content-Type') == 'application/atom+xml'


@pytest.mark.django_db
def test_app_agent_post_without_identifier_content(rf, app_agent_xml):
    identifier, xml = app_agent_xml
    request = rf.post('/', xml, content_type='application/xml')
    response = views.app_agent(request)
    assert identifier in response.content


@pytest.mark.xfail(reason='POST request without body raises uncaught exception.')
def test_app_agent_post_without_body_without_identifier_is_handled(rf):
    request = rf.post('/')
    views.app_agent(request)


def test_app_agent_without_identifier_returns_bad_request(rf):
    request = rf.head('/')
    response = views.app_agent(request)
    assert response.status_code == 400


def test_app_agent_with_identifier_returns_not_found(rf):
    request = rf.get('/')
    response = views.app_agent(request, 'fake-identifier')
    assert response.status_code == 404


@pytest.mark.django_db
def test_app_agent_delete_with_identifier_returns_ok(rf):
    agent = factories.AgentFactory.create()
    request = rf.delete('/')
    response = views.app_agent(request, agent.agent_identifier)
    assert response.status_code == 200


@pytest.mark.django_db
def test_app_agent_delete_with_identifier_removes_agent(rf):
    agent = factories.AgentFactory.create()
    request = rf.delete('/')
    views.app_agent(request, agent.agent_identifier)
    assert models.Agent.objects.count() == 0


@pytest.mark.django_db
def test_app_agent_put_with_identifier_returns_ok(app_agent_xml, rf):
    identifier, xml = app_agent_xml
    agent = factories.AgentFactory.create(agent_identifier=identifier)

    request = rf.put('/', xml, content_type='application/xml')
    response = views.app_agent(request, agent.agent_identifier)
    assert response.status_code == 200


@pytest.mark.django_db
def test_app_agent_put_with_identifier_content_type(app_agent_xml, rf):
    identifier, xml = app_agent_xml
    agent = factories.AgentFactory.create(agent_identifier=identifier)

    request = rf.put('/', xml, content_type='application/xml')
    response = views.app_agent(request, agent.agent_identifier)
    assert response.get('Content-Type') == 'application/atom+xml'


@pytest.mark.django_db
def test_app_agent_put_with_identifier_agent_updated(app_agent_xml, rf):
    identifier, xml = app_agent_xml
    agent = factories.AgentFactory.create(agent_identifier=identifier)

    request = rf.put('/', xml, content_type='application/xml')
    views.app_agent(request, agent.agent_identifier)

    updated_agent = models.Agent.objects.get(agent_identifier=identifier)
    assert updated_agent.agent_name != agent.agent_name


@pytest.mark.django_db
def test_app_agent_put_with_identifier_content(app_agent_xml, rf):
    identifier, xml = app_agent_xml
    agent = factories.AgentFactory.create(agent_identifier=identifier)

    request = rf.put('/', xml, content_type='application/xml')
    response = views.app_agent(request, agent.agent_identifier)

    updated_agent = models.Agent.objects.get(agent_identifier=identifier)

    assert updated_agent.agent_name in response.content
    assert updated_agent.agent_type in response.content


@pytest.mark.django_db
def test_app_agent_get_with_identifier_returns_ok(rf):
    agent = factories.AgentFactory.create()
    request = rf.get('/')
    response = views.app_agent(request, agent.agent_identifier)
    assert response.status_code == 200


@pytest.mark.django_db
def test_app_agent_get_with_identifier_content_type(rf):
    agent = factories.AgentFactory.create()
    request = rf.get('/')
    response = views.app_agent(request, agent.agent_identifier)
    assert response.get('Content-Type') == 'application/atom+xml'


@pytest.mark.django_db
def test_app_agent_get_with_identifier_content(rf):
    agent = factories.AgentFactory.create()
    request = rf.get('/')
    response = views.app_agent(request, agent.agent_identifier)
    assert agent.agent_identifier in response.content
