import json

import pytest
from lxml import objectify

from django.http import Http404
from django.utils import timezone
from django.core.urlresolvers import reverse

from premis_event_service import views, models
from . import factories, AppEventTestXml


pytestmark = [
    pytest.mark.urls('premis_event_service.urls'),
    pytest.mark.django_db,
]


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


def test_humanEvent_raises_http404(rf):
    request = rf.get('/')
    with pytest.raises(Http404):
        views.humanEvent(request)


def test_humanEvent_returns_ok(rf):
    event = factories.EventFactory.create()
    request = rf.get('/')
    response = views.humanEvent(request, event.event_identifier)
    assert response.status_code == 200


def test_json_event_list_returns_ok(rf):
    factories.EventFactory.create_batch(30)
    request = rf.get('/')
    response = views.recent_event_list(request)
    assert response.status_code == 200


def test_json_event_list_context(client):
    num_events = 30
    factories.EventFactory.create_batch(num_events)
    response = client.get(reverse('premis_event_service.views.recent_event_list'))

    context = response.context[-1]
    assert len(context['entries']) == 10
    assert context['num_events'] == num_events


def test_json_event_list_with_no_events(rf):
    request = rf.get('/')
    response = views.recent_event_list(request)
    assert response.status_code == 200


def test_json_agent_returns_ok(rf):
    agent = factories.AgentFactory.create()
    request = rf.get('/')
    response = views.json_agent(request, agent.agent_identifier)
    assert response.status_code == 200
    assert response.get('Content-Type') == 'application/json'


def test_json_agent_payload(rf):
    agent = factories.AgentFactory.create()
    request = rf.get('/')
    response = views.json_agent(request, agent.agent_identifier)
    payload = json.loads(response.content)

    assert agent.get_absolute_url() in payload['id']
    assert payload['type'] == agent.agent_type
    assert payload['name'] == agent.agent_name
    assert payload['note'] == agent.agent_note


def test_agent_xml_returns_ok(rf):
    agent = factories.AgentFactory.create()
    request = rf.get('/')
    response = views.agentXML(request, agent.agent_identifier)
    assert response.status_code == 200


def test_agent_xml_returns_not_found(rf):
    identifier = 'ark:/00001/dne'
    request = rf.get('/')
    response = views.agentXML(request, identifier)
    assert response.status_code == 404


def test_agent_xml_content_type(rf):
    agent = factories.AgentFactory.create()
    request = rf.get('/')
    response = views.agentXML(request, agent.agent_identifier)
    assert response.get('Content-Type') == 'application/atom+xml'


def test_agent_xml_returns_ok_with_premis_identifier(rf):
    # Create an agent and update the identifier to include `.premis`.
    agent = factories.AgentFactory.create()
    agent.identifier = 'ark:/00001/coda1n.premis'
    agent.save()

    request = rf.get('/.premis')
    response = views.agentXML(request, agent.agent_identifier)

    assert response.status_code == 200


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


def test_find_event_returns_ok(rf):
    event = factories.EventFactory.create(linking_objects=True)
    request = rf.get('/')
    linking_object = event.linking_objects.first()
    response = views.findEvent(request, linking_object.object_identifier)
    assert response.status_code == 200


def test_find_event_response_content_type(rf):
    event = factories.EventFactory.create(linking_objects=True)
    request = rf.get('/')
    linking_object = event.linking_objects.first()
    response = views.findEvent(request, linking_object.object_identifier)

    assert response.get('Content-Type') == 'application/atom+xml'


def test_find_event_returns_not_found(rf):
    request = rf.get('/')
    response = views.findEvent(request, 'fake-identifier')
    assert response.status_code == 404


def test_find_event_finds_multiple_events(rf):
    # Create two events. Specify a datetime for the second event to assert
    # that the two events will not end up with the same event_date_time. We
    # will use that attribute to sort them later.
    datetime_obj = timezone.now().replace(year=2015, month=1, day=1)
    event1 = factories.EventFactory.create(linking_objects=True)
    event2 = factories.EventFactory.create(event_date_time=datetime_obj)

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


class TestAppAgent:

    def test_list_returns_ok(self, rf):
        request = rf.get('/')
        response = views.app_agent(request)
        assert response.status_code == 200

    def test_list_content_type(self, rf):
        request = rf.get('/')
        response = views.app_agent(request)
        assert response.get('Content-Type') == 'application/atom+xml'

    @pytest.mark.xfail(reason='EmptyPage exception is not handled.')
    def test_list_with_invalid_page(self, rf):
        request = rf.get('/?page=3')
        views.app_agent(request)

    @pytest.fixture
    def app_agent_xml(self, ):
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

    def test_post_without_identifier_returns_created(self, rf, app_agent_xml):
        _, xml = app_agent_xml
        request = rf.post('/', xml, content_type='application/xml')
        response = views.app_agent(request)
        assert response.status_code == 201

    def test_post_without_identifier_content_type(self, rf, app_agent_xml):
        _, xml = app_agent_xml
        request = rf.post('/', xml, content_type='application/xml')
        response = views.app_agent(request)
        assert response.get('Content-Type') == 'application/atom+xml'

    def test_post_without_identifier_content(self, rf, app_agent_xml):
        identifier, xml = app_agent_xml
        request = rf.post('/', xml, content_type='application/xml')
        response = views.app_agent(request)
        assert identifier in response.content

    @pytest.mark.xfail(reason='POST request without body raises uncaught exception.')
    def test_post_without_body_without_identifier_is_handled(self, rf):
        request = rf.post('/')
        views.app_agent(request)

    def test_returns_bad_request(self, rf):
        request = rf.head('/')
        response = views.app_agent(request)
        assert response.status_code == 400

    def test_get_with_invalid_identifier_returns_not_found(self, rf):
        request = rf.get('/')
        response = views.app_agent(request, 'fake-identifier')
        assert response.status_code == 404

    def test_delete_with_identifier_returns_ok(self, rf):
        agent = factories.AgentFactory.create()
        request = rf.delete('/')
        response = views.app_agent(request, agent.agent_identifier)
        assert response.status_code == 200

    def test_delete_with_identifier_removes_agent(self, rf):
        agent = factories.AgentFactory.create()
        request = rf.delete('/')
        views.app_agent(request, agent.agent_identifier)
        assert models.Agent.objects.count() == 0

    def test_put_with_identifier_returns_ok(self, app_agent_xml, rf):
        identifier, xml = app_agent_xml
        agent = factories.AgentFactory.create(agent_identifier=identifier)

        request = rf.put('/', xml, content_type='application/xml')
        response = views.app_agent(request, agent.agent_identifier)
        assert response.status_code == 200

    def test_put_with_identifier_content_type(self, app_agent_xml, rf):
        identifier, xml = app_agent_xml
        agent = factories.AgentFactory.create(agent_identifier=identifier)

        request = rf.put('/', xml, content_type='application/xml')
        response = views.app_agent(request, agent.agent_identifier)
        assert response.get('Content-Type') == 'application/atom+xml'

    def test_put_with_identifier_agent_updated(self, app_agent_xml, rf):
        identifier, xml = app_agent_xml
        agent = factories.AgentFactory.create(agent_identifier=identifier)

        request = rf.put('/', xml, content_type='application/xml')
        views.app_agent(request, agent.agent_identifier)

        updated_agent = models.Agent.objects.get(agent_identifier=identifier)
        assert updated_agent.agent_name != agent.agent_name

    def test_put_with_identifier_content(self, app_agent_xml, rf):
        identifier, xml = app_agent_xml
        agent = factories.AgentFactory.create(agent_identifier=identifier)

        request = rf.put('/', xml, content_type='application/xml')
        response = views.app_agent(request, agent.agent_identifier)

        updated_agent = models.Agent.objects.get(agent_identifier=identifier)

        assert updated_agent.agent_name in response.content
        assert updated_agent.agent_type in response.content

    def test_get_with_identifier_returns_ok(self, rf):
        agent = factories.AgentFactory.create()
        request = rf.get('/')
        response = views.app_agent(request, agent.agent_identifier)
        assert response.status_code == 200

    def test_get_with_identifier_content_type(self, rf):
        agent = factories.AgentFactory.create()
        request = rf.get('/')
        response = views.app_agent(request, agent.agent_identifier)
        assert response.get('Content-Type') == 'application/atom+xml'

    def test_get_with_identifier_content(self, rf):
        agent = factories.AgentFactory.create()
        request = rf.get('/')
        response = views.app_agent(request, agent.agent_identifier)
        assert agent.agent_identifier in response.content


class TestAppEvent:

    @pytest.fixture
    def app_event_xml(self):
        with AppEventTestXml() as f:
            xml = f.read()
        identifier = '6939fb9e-2bf1-4bff-a06a-71c0fc41a9aa'
        return identifier, xml.format(identifier=identifier)

    def test_post_returns_created(self, app_event_xml, rf):
        _, xml = app_event_xml
        request = rf.post('/', xml, content_type='application/xml', HTTP_HOST='example.com')
        response = views.app_event(request)
        assert response.status_code == 201

    def test_post_response_content_type(self, app_event_xml, rf):
        _, xml = app_event_xml
        request = rf.post('/', xml, content_type='application/xml', HTTP_HOST='example.com')
        response = views.app_event(request)
        assert response.get('Content-Type') == 'application/atom+xml'

    def test_post_response_content(self, app_event_xml, rf):
        identifier, xml = app_event_xml
        request = rf.post('/', xml, content_type='application/xml', HTTP_HOST='example.com')
        response = views.app_event(request)
        assert identifier in response.content

    def test_post_creates_event(self, app_event_xml, rf):
        assert models.Event.objects.count() == 0
        _, xml = app_event_xml
        request = rf.post('/', xml, content_type='application/xml', HTTP_HOST='example.com')
        views.app_event(request)
        assert models.Event.objects.count() == 1

    @pytest.mark.xfail(reason='Call to updateObjectFromXML fails unexpectedly.')
    def test_put_returns_ok(self, app_event_xml, rf):
        identifier, xml = app_event_xml
        factories.EventFactory.create(event_identifier=identifier)

        request = rf.put('/', xml, content_type='application/xml', HTTP_HOST='example.com')
        response = views.app_event(request, identifier)

        assert response.status_code == 200

    @pytest.mark.xfail(reason='Call to updateObjectFromXML fails unexpectedly.')
    def test_put_response_content_type(self, app_event_xml, rf):
        identifier, xml = app_event_xml
        factories.EventFactory.create(event_identifier=identifier)

        request = rf.put('/', xml, content_type='application/xml', HTTP_HOST='example.com')
        response = views.app_event(request, identifier)

        assert response.get('Content-Type') == 'application/atom+xml'

    def test_list_returns_ok(self, rf):
        factories.EventFactory.create_batch(30)
        request = rf.get('/')
        response = views.app_event(request)
        assert response.status_code == 200

    def test_list_number_of_events(self, rf):
        factories.EventFactory.create_batch(30)
        request = rf.get('/')
        response = views.app_event(request)
        xml = objectify.fromstring(response.content)

        num_events = 20
        assert len(xml.entry) == num_events

    @pytest.mark.xfail(reason='Global name DATE_FORMAT is not defined.')
    def test_list_filtering_by_start_date(self, rf):
        datetime_obj = timezone.now().replace(2015, 1, 1)
        factories.EventFactory.create_batch(30, event_date_time=datetime_obj)
        event = factories.EventFactory.create(event_date_time=timezone.now())

        request = rf.get('/?start_date=01/31/2015')
        response = views.app_event(request)

        xml = objectify.fromstring(response.content)
        num_events = 1

        assert len(xml.entry) == num_events
        assert event.event_identifier in response.content

    @pytest.mark.xfail(reason='Global name DATE_FORMAT is not defined.')
    def test_list_filtering_by_end_date(self, rf):
        datetime_obj = timezone.now().replace(2015, 1, 1)
        factories.EventFactory.create_batch(30, event_date_time=timezone.now())
        event = factories.EventFactory.create(event_date_time=datetime_obj)

        request = rf.get('/?end_date=01/31/2015')
        response = views.app_event(request)

        xml = objectify.fromstring(response.content)
        num_events = 1

        assert len(xml.entry) == num_events
        assert event.event_identifier in response.content

    def test_list_filtering_by_linking_object_id(self, rf):
        factories.EventFactory.create_batch(30)
        event = factories.EventFactory.create(linking_objects=True)
        linking_object = event.linking_objects.first()

        url = '/?link_object_id={0}'.format(linking_object.object_identifier)
        request = rf.get(url)
        response = views.app_event(request)

        xml = objectify.fromstring(response.content)
        num_events = 1

        assert len(xml.entry) == num_events
        assert event.event_identifier in response.content

    def test_list_filtering_by_event_outcome(self, rf):
        factories.EventFactory.create_batch(30)

        event_outcome = 'success'
        event = factories.EventFactory.create(event_outcome=event_outcome)

        request = rf.get('?outcome={0}'.format(event_outcome))
        response = views.app_event(request)

        xml = objectify.fromstring(response.content)
        num_events = 1

        assert len(xml.entry) == num_events
        assert event.event_identifier in response.content

    def test_list_filtering_by_event_type(self, rf):
        factories.EventFactory.create_batch(30)

        event_type = 'Test Type'
        event = factories.EventFactory.create(event_type=event_type)

        request = rf.get('?type={0}'.format(event_type))
        response = views.app_event(request)

        xml = objectify.fromstring(response.content)
        num_events = 1

        assert len(xml.entry) == num_events
        assert event.event_identifier in response.content

    def test_get_with_identifier_returns_ok(self, rf):
        event = factories.EventFactory.create()
        request = rf.get('/', HTTP_HOST='example.com')
        response = views.app_event(request, event.event_identifier)
        assert response.status_code == 200

    def test_get_with_identifier_returns_not_found(self, rf):
        request = rf.get('/', HTTP_HOST='example.com')
        response = views.app_event(request, 'ark:/00001/dne')
        assert response.status_code == 404

    def test_get_with_identifier_content_type(self, rf):
        event = factories.EventFactory.create()
        request = rf.get('/', HTTP_HOST='example.com')
        response = views.app_event(request, event.event_identifier)
        assert response.get('Content-Type') == 'application/atom+xml'

    def test_get_with_identifier_content(self, rf):
        event = factories.EventFactory.create()
        request = rf.get('/', HTTP_HOST='example.com')
        response = views.app_event(request, event.event_identifier)
        assert event.event_identifier in response.content

    def test_delete_with_identifier_returns_ok(self, rf):
        event = factories.EventFactory.create()
        request = rf.delete('/', HTTP_HOST='example.com')
        response = views.app_event(request, event.event_identifier)
        assert response.status_code == 200

    def test_delete_with_identifier_returns_not_found(self, rf):
        request = rf.delete('/', HTTP_HOST='example.com')
        response = views.app_event(request, 'ark:/00001/dne')
        assert response.status_code == 404

    def test_delete_with_identifier_content_type(self, rf):
        event = factories.EventFactory.create()
        request = rf.delete('/', HTTP_HOST='example.com')
        response = views.app_event(request, event.event_identifier)
        assert response.get('Content-Type') == 'application/atom+xml'

    def test_delete_with_identifier_content(self, rf):
        event = factories.EventFactory.create()
        request = rf.delete('/', HTTP_HOST='example.com')
        response = views.app_event(request, event.event_identifier)
        assert event.event_identifier in response.content

    def test_delete_with_identifier_removes_event(self, rf):
        event = factories.EventFactory.create()
        request = rf.delete('/', HTTP_HOST='example.com')
        views.app_event(request, event.event_identifier)
        assert models.Agent.objects.count() == 0


class TestEventSearch:

    def response_has_event(self, response, event):
        paginated_entries = response.context[-1]['entries']
        filtered_entry = paginated_entries.object_list[0]

        if not len(paginated_entries.object_list) == 1:
            return False

        if not filtered_entry.event_identifier == event.event_identifier:
            return False
        return True

    def test_returns_ok(self, rf):
        request = rf.get('/')
        response = views.event_search(request)
        assert response.status_code == 200

    def test_filter_by_start_date(self, client):
        datetime_obj = timezone.now().replace(2015, 1, 1)
        factories.EventFactory.create_batch(30, event_date_time=datetime_obj)
        event = factories.EventFactory.create(event_date_time=timezone.now())

        query_string = '?start_date=01/31/2015'
        url = reverse('premis_event_service.views.event_search')
        response = client.get(url + query_string)

        assert self.response_has_event(response, event)

    def test_filter_by_end_date(self, client):
        datetime_obj = timezone.now().replace(2015, 1, 1)
        factories.EventFactory.create_batch(30, event_date_time=timezone.now())
        event = factories.EventFactory.create(event_date_time=datetime_obj)

        query_string = '?end_date=01/31/2015'
        url = reverse('premis_event_service.views.event_search')
        response = client.get(url + query_string)

        assert self.response_has_event(response, event)

    @pytest.mark.xfail
    def test_filter_by_linked_object_id(self, client):
        factories.EventFactory.create_batch(30)
        event = factories.EventFactory.create(linking_objects=True)
        linking_object = event.linking_objects.first()

        query_string = '?linked_object_id={0}'.format(linking_object.object_identifier)
        url = reverse('premis_event_service.views.event_search')
        response = client.get(url + query_string)

        assert self.response_has_event(response, event)

    def test_filter_by_outcome(self, client):
        event_outcome = 'Test outcome'
        factories.EventFactory.create_batch(30)
        event = factories.EventFactory.create(event_outcome=event_outcome)

        query_string = '?outcome={0}'.format(event_outcome)
        url = reverse('premis_event_service.views.event_search')
        response = client.get(url + query_string)

        assert self.response_has_event(response, event)

    def test_filter_by_event_type(self, client):
        event_type = 'Test Event Type'
        factories.EventFactory.create_batch(30)
        event = factories.EventFactory.create(event_type=event_type)

        query_string = '?event_type={0}'.format(event_type)
        url = reverse('premis_event_service.views.event_search')
        response = client.get(url + query_string)

        assert self.response_has_event(response, event)
