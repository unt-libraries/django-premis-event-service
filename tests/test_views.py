import json
import random

from lxml import objectify
import pytest

from django.urls import reverse
from django.http import Http404
from django.utils.http import urlquote
from datetime import datetime

from premis_event_service import views, models
from premis_event_service.settings import EVENT_TYPE_CHOICES, EVENT_OUTCOME_CHOICES
from . import factories


pytestmark = [
    pytest.mark.urls('premis_event_service.urls'),
    pytest.mark.django_db,
]


def test_app_returns_ok(rf):
    request = rf.get('/')
    response = views.app(request)
    assert response.status_code == 200


def test_app_response_content_type(rf):
    request = rf.get('/')
    response = views.app(request)
    assert response.get('Content-Type') == 'application/atom+xml'


def test_humanEvent_raises_http404(rf):
    """An Http404 should be raised when the view is unable to locate
    an Event.
    """
    request = rf.get('/')
    with pytest.raises(Http404):
        views.humanEvent(request)


def test_humanEvent_returns_ok(rf):
    event = factories.EventFactory.create()
    request = rf.get('/')
    response = views.humanEvent(request, event.event_identifier)
    assert response.status_code == 200


def test_humanAgent_returns_ok(rf):
    agent = factories.AgentFactory.create()
    request = rf.get('/')
    response = views.humanAgent(request, agent.agent_identifier)
    assert response.status_code == 200


def test_humanAgent_with_invalid_identifier(rf):
    request = rf.get('/')
    response = views.humanAgent(request, 'test-identifier')
    assert response.status_code == 404


def test_humanAgent_returns_all_agents(client):
    factories.AgentFactory.create_batch(30)
    response = client.get(
            reverse('agent-list'))
    view_context = response.context[-1]
    assert len(view_context['agents']) == models.Agent.objects.count()


def test_humanAgent_with_identifier(client):
    agent = factories.AgentFactory.create()
    response = client.get(
            reverse('agent-detail', args=[agent.agent_identifier]))
    context_agent = response.context[-1]['agents'][0]
    assert agent.agent_identifier == context_agent['agent_identifier']


def test_recent_event_list_returns_ok(rf):
    factories.EventFactory.create_batch(30)
    request = rf.get('/')
    response = views.recent_event_list(request)
    assert response.status_code == 200


def test_recent_event_list_context(client):
    """Test the Events in the response context."""
    num_events = 30
    factories.EventFactory.create_batch(num_events)
    response = client.get(reverse('event-list'))

    context = response.context[-1]
    assert len(context['entries']) == 10
    assert context['num_events'] == num_events


def test_recent_event_list_with_no_events(rf):
    """Test that the response has a status code 200 when there are no
    Events in the database.
    """
    request = rf.get('/')
    response = views.recent_event_list(request)
    assert response.status_code == 200


def test_json_agent_returns_ok(rf):
    agent = factories.AgentFactory.create()
    request = rf.get('/')
    response = views.json_agent(request, agent.agent_identifier)
    assert response.status_code == 200


def test_json_agent_raises_Http404(rf):
    request = rf.get('/')
    with pytest.raises(Http404):
        views.json_agent(request, 'test-identifier')


def test_json_agent_response_content_type(rf):
    agent = factories.AgentFactory.create()
    request = rf.get('/')
    response = views.json_agent(request, agent.agent_identifier)
    assert response.get('Content-Type') == 'application/json'


def test_json_agent_payload(rf):
    """Verify that the json output matches the Agent attributes."""
    agent = factories.AgentFactory.create()
    request = rf.get('/')
    response = views.json_agent(request, agent.agent_identifier)
    payload = json.loads(response.content.decode('utf-8'))

    assert agent.get_absolute_url() in payload['id']
    assert payload['type'] == agent.agent_type
    assert payload['name'] == agent.agent_name
    assert payload['note'] == agent.agent_note


def test_agentXML_returns_ok(rf):
    agent = factories.AgentFactory.create()
    request = rf.get('/')
    response = views.agentXML(request, agent.agent_identifier)
    assert response.status_code == 200


def test_agentXML_returns_not_found(rf):
    # ark:/00001/dne is a non-existent identifier.
    identifier = 'ark:/00001/dne'
    request = rf.get('/')
    response = views.agentXML(request, identifier)
    assert response.status_code == 404


def test_agentXML_response_content_type(rf):
    agent = factories.AgentFactory.create()
    request = rf.get('/')
    response = views.agentXML(request, agent.agent_identifier)
    assert response.get('Content-Type') == 'application/atom+xml'


def test_agentXML_returns_ok_with_premis_identifier(rf):
    # Create an agent and update the identifier to include `.premis`.
    agent = factories.AgentFactory.create()
    agent.identifier = 'ark:/00001/coda1n.premis'
    agent.save()

    request = rf.get('/.premis')
    response = views.agentXML(request, agent.agent_identifier)

    assert response.status_code == 200


def test_agentXML_returns_not_found_with_premis_identifier(rf):
    identifier = 'ark:/00001/coda1n.premis'
    request = rf.get('/.premis')
    response = views.agentXML(request, identifier)
    assert response.status_code == 404


def test_eventXML(rf):
    request = rf.get('/')
    response = views.eventXML(request)
    assert response.status_code == 200
    assert b"So you would like XML for the event with identifier" in \
           response.content


def test_findEvent_returns_ok(rf):
    event = factories.EventFactory.create(linking_objects=True)
    request = rf.get('/')
    linking_object = event.linking_objects.first()
    response = views.findEvent(request, linking_object.object_identifier)
    assert response.status_code == 200


def test_findEvent_response_content_type(rf):
    event = factories.EventFactory.create(linking_objects=True)
    request = rf.get('/')
    linking_object = event.linking_objects.first()
    response = views.findEvent(request, linking_object.object_identifier)

    assert response.get('Content-Type') == 'application/atom+xml'


def test_findEvent_returns_not_found(rf):
    request = rf.get('/')
    response = views.findEvent(request, 'fake-identifier')
    assert response.status_code == 404


def test_findEvent_finds_multiple_events(rf):
    """Check that findEvent returns the newest event if a LinkObject is
    associated with multiple Events.
    """
    # Create two events. Specify a datetime for the second event to assert
    # that the two events will not end up with the same event_date_time. We
    # will use that attribute to sort them later.
    datetime_obj = datetime.now().replace(year=2015, month=1, day=1)
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
    assert old_event.event_identifier in response.content.decode('utf-8')
    assert new_event.event_identifier not in response.content.decode('utf-8')


class TestAppAgent:
    """Tests for views.app_agent."""
    CONTENT_TYPE = 'application/atom+xml'

    def test_list_returns_ok(self, rf):
        request = rf.get('/')
        response = views.app_agent(request)
        assert response.status_code == 200

    def test_list_response_content_type(self, rf):
        request = rf.get('/')
        response = views.app_agent(request)
        assert response.get('Content-Type') == self.CONTENT_TYPE

    @pytest.mark.xfail(reason='EmptyPage exception is not handled.')
    def test_list_with_invalid_page(self, rf):
        request = rf.get('/?page=3')
        views.app_agent(request)

    def test_post_returns_created(self, rf, agent_xml):
        request = rf.post('/', agent_xml.obj_xml, content_type='application/xml')
        response = views.app_agent(request)
        assert response.status_code == 201

    def test_post_response_content_type(self, rf, agent_xml):
        request = rf.post('/', agent_xml.obj_xml, content_type='application/xml')
        response = views.app_agent(request)
        assert response.get('Content-Type') == self.CONTENT_TYPE

    def test_post_response_content(self, rf, agent_xml):
        request = rf.post('/', agent_xml.obj_xml, content_type='application/xml')
        response = views.app_agent(request)

        identifier = agent_xml.identifier
        assert identifier in response.content.decode('utf-8')

    @pytest.mark.xfail(reason='POST request without body raises uncaught exception.')
    def test_post_without_body_is_handled(self, rf):
        request = rf.post('/')
        views.app_agent(request)

    def test_put_without_identifier_returns_bad_request(self, rf):
        request = rf.put('/')
        response = views.app_agent(request)
        assert response.status_code == 400

    def test_delete_without_identifier_returns_bad_request(self, rf):
        request = rf.delete('/')
        response = views.app_agent(request)
        assert response.status_code == 400

    def test_invalid_identifier_returns_not_found(self, rf):
        """Test that a nonexistent Agent identifier results in a
        404 Not Found.
        """
        request = rf.get('/')
        response = views.app_agent(request, 'fake-identifier')
        assert response.status_code == 404

    def test_delete_returns_ok(self, rf):
        agent = factories.AgentFactory.create()
        request = rf.delete('/')
        response = views.app_agent(request, agent.agent_identifier)
        assert response.status_code == 200

    def test_delete_removes_agent(self, rf):
        agent = factories.AgentFactory.create()
        request = rf.delete('/')
        views.app_agent(request, agent.agent_identifier)
        assert models.Agent.objects.count() == 0

    def test_put_returns_ok(self, agent_xml, rf):
        identifier = agent_xml.identifier
        agent = factories.AgentFactory.create(agent_identifier=identifier)

        request = rf.put('/', agent_xml.obj_xml, content_type='application/xml')
        response = views.app_agent(request, agent.agent_identifier)
        assert response.status_code == 200

    def test_put_response_content_type(self, agent_xml, rf):
        identifier = agent_xml.identifier
        agent = factories.AgentFactory.create(agent_identifier=identifier)

        request = rf.put('/', agent_xml.obj_xml, content_type='application/xml')
        response = views.app_agent(request, agent.agent_identifier)
        assert response.get('Content-Type') == self.CONTENT_TYPE

    def test_put_agent_updated(self, agent_xml, rf):
        identifier = agent_xml.identifier
        agent = factories.AgentFactory.create(agent_identifier=identifier)

        request = rf.put('/', agent_xml.obj_xml, content_type='application/xml')
        views.app_agent(request, agent.agent_identifier)

        updated_agent = models.Agent.objects.get(agent_identifier=identifier)
        assert updated_agent.agent_name != agent.agent_name

    def test_put_response_content(self, agent_xml, rf):
        identifier = agent_xml.identifier
        agent = factories.AgentFactory.create(agent_identifier=identifier)

        request = rf.put('/', agent_xml.obj_xml, content_type='application/xml')
        response = views.app_agent(request, agent.agent_identifier)

        updated_agent = models.Agent.objects.get(agent_identifier=identifier)

        assert updated_agent.agent_name in response.content.decode('utf-8')
        assert updated_agent.agent_type in response.content.decode('utf-8')

    def test_get_with_identifier_returns_ok(self, rf):
        agent = factories.AgentFactory.create()
        request = rf.get('/')
        response = views.app_agent(request, agent.agent_identifier)
        assert response.status_code == 200

    def test_get_with_identifier_response_content_type(self, rf):
        agent = factories.AgentFactory.create()
        request = rf.get('/')
        response = views.app_agent(request, agent.agent_identifier)
        assert response.get('Content-Type') == self.CONTENT_TYPE

    def test_get_with_identifier_response_content(self, rf):
        agent = factories.AgentFactory.create()
        request = rf.get('/')
        response = views.app_agent(request, agent.agent_identifier)
        assert agent.agent_identifier in response.content.decode('utf-8')

    def test_head_without_identifier(self, rf):
        request = rf.head('/')
        response = views.app_agent(request)
        assert response.content == b'', b'The message body must be empty'
        assert response.status_code == 200

    def test_head_and_get_headers_match_without_identifier(self, rf):
        head_request, get_request = rf.head('/'), rf.get('/')

        head_response = views.app_agent(head_request)
        get_response = views.app_agent(get_request)

        expected_headers = get_response.serialize_headers()
        actual_headers = head_response.serialize_headers()

        assert expected_headers == actual_headers, 'The response headers do not match.'

    def test_head_with_identifier(self, rf):
        agent = factories.AgentFactory.create()
        request = rf.head('/')
        response = views.app_agent(request, agent.agent_identifier)
        assert response.content == b'', b'The message body must be empty'
        assert response.status_code == 200

    def test_head_and_get_headers_match_with_identifier(self, rf):
        agent = factories.AgentFactory.create()
        head_request, get_request = rf.head('/'), rf.get('/')

        head_response = views.app_agent(head_request, agent.agent_identifier)
        get_response = views.app_agent(get_request, agent.agent_identifier)

        expected_headers = get_response.serialize_headers()
        actual_headers = head_response.serialize_headers()

        assert expected_headers == actual_headers, 'The response headers do not match.'


class TestAppEvent:
    """Tests for views.app_event."""
    CONTENT_TYPE = 'application/atom+xml'
    RESULTS_PER_PAGE = views.EVENT_SEARCH_PER_PAGE

    def response_has_event(self, response, event):
        """True if the event is the only event in the response content."""
        xml = objectify.fromstring(response.content)
        if len(xml.entry) != 1:
            return False
        if event.event_identifier not in response.content.decode('utf-8'):
            return False
        return True

    def response_includes_event(self, response, event):
        return event.event_identifier in response.content.decode('utf-8')

    def test_post_returns_created(self, event_xml, rf):
        request = rf.post(
            '/',
            event_xml.entry_xml,
            content_type='application/xml',
            HTTP_HOST='example.com')

        response = views.app_event(request)
        assert response.status_code == 201

    def test_post_response_content_type(self, event_xml, rf):
        request = rf.post(
            '/',
            event_xml.entry_xml,
            content_type='application/xml',
            HTTP_HOST='example.com')

        response = views.app_event(request)
        assert response.get('Content-Type') == self.CONTENT_TYPE

    def test_post_response_content(self, event_xml, rf):
        request = rf.post(
            '/',
            event_xml.entry_xml,
            content_type='application/xml',
            HTTP_HOST='example.com')

        response = views.app_event(request)
        identifier = event_xml.identifier
        assert identifier in response.content.decode('utf-8')

    def test_post_creates_event(self, event_xml, rf):
        assert models.Event.objects.count() == 0
        request = rf.post(
            '/',
            event_xml.entry_xml,
            content_type='application/xml',
            HTTP_HOST='example.com')

        views.app_event(request)
        assert models.Event.objects.count() == 1

    def test_post_DuplicateEventError(self, event_xml, rf):
        request = rf.post(
            '/',
            event_xml.entry_xml,
            content_type='application/xml',
            HTTP_HOST='example.com')

        # Try to POST the same event twice.
        views.app_event(request)
        response = views.app_event(request)
        assert response.status_code == 409
        expected_response = "An event with id='{}' exists.".format(event_xml.identifier)
        assert expected_response in response.content.decode('utf-8')

    def test_put_returns_ok(self, event_xml, rf):
        identifier = event_xml.identifier
        factories.EventFactory.create(event_identifier=identifier)

        request = rf.put(
            '/',
            event_xml.entry_xml,
            content_type='application/xml',
            HTTP_HOST='example.com')

        response = views.app_event(request, identifier)

        assert response.status_code == 200

    def test_put_response_content_type(self, event_xml, rf):
        identifier = event_xml.identifier
        factories.EventFactory.create(event_identifier=identifier)

        request = rf.put(
            '/',
            event_xml.entry_xml,
            content_type='application/xml',
            HTTP_HOST='example.com')

        response = views.app_event(request, identifier)

        assert response.get('Content-Type') == self.CONTENT_TYPE

    def test_list_returns_ok(self, rf):
        factories.EventFactory.create_batch(30)
        request = rf.get('/')
        response = views.app_event(request)
        assert response.status_code == 200

    def test_list_number_of_events(self, rf):
        factories.EventFactory.create_batch(self.RESULTS_PER_PAGE * 2)
        request = rf.get('/')
        response = views.app_event(request)
        xml = objectify.fromstring(response.content.decode('utf-8'))
        assert len(xml.entry) == self.RESULTS_PER_PAGE

    @pytest.mark.xfail(reason='Global name DATE_FORMAT is not defined.')
    def test_list_filtering_by_start_date(self, rf):
        datetime_obj = datetime.now().replace(2015, 1, 1)
        factories.EventFactory.create_batch(30, event_date_time=datetime_obj)
        event = factories.EventFactory.create(event_date_time=datetime.now())

        request = rf.get('/?start_date=01/31/2015')
        response = views.app_event(request)
        assert self.response_has_event(response, event)

    @pytest.mark.xfail(reason='Global name DATE_FORMAT is not defined.')
    def test_list_filtering_by_end_date(self, rf):
        datetime_obj = datetime.now().replace(2015, 1, 1)
        factories.EventFactory.create_batch(30, event_date_time=datetime.now())
        event = factories.EventFactory.create(event_date_time=datetime_obj)

        request = rf.get('/?end_date=01/31/2015')
        response = views.app_event(request)
        assert self.response_has_event(response, event)

    def test_list_filtering_by_linking_object_id(self, rf):
        factories.EventFactory.create_batch(30)
        event = factories.EventFactory.create(linking_objects=True)
        linking_object = event.linking_objects.first()

        url = '/?link_object_id={0}'.format(linking_object.object_identifier)
        request = rf.get(url)
        response = views.app_event(request)
        assert self.response_has_event(response, event)

    def test_list_filtering_by_event_outcome(self, rf):
        factories.EventFactory.create_batch(30)

        event_outcome = 'success'
        event = factories.EventFactory.create(event_outcome=event_outcome)

        request = rf.get('?outcome={0}'.format(event_outcome))
        response = views.app_event(request)
        assert self.response_has_event(response, event)

    def test_list_filtering_by_event_type(self, rf):
        factories.EventFactory.create_batch(10)

        event_type = random.choice(EVENT_TYPE_CHOICES)[0]
        event = factories.EventFactory.create(event_type=event_type)

        request = rf.get('?event_type={0}'.format(urlquote(event_type)))
        response = views.app_event(request)
        assert self.response_includes_event(response, event)

    @pytest.mark.xfail(reason='Not implemented.')
    def test_list_ordering_ascending(self, rf):
        events = factories.EventFactory.create_batch(3)
        events.sort(key=lambda e: e.event_identifier)

        # Order by the Event identifier because the values are globally unique.
        # Pure Python vs the Django ORM sort items with matching keys differently.
        request = rf.get('?orderby=event_identifier')
        response = views.app_event(request)

        list_events = objectify.fromstring(response.content).entry
        ordered_event_ids = [f.title for f in list_events]
        event_ids = [f.event_identifier for f in events]

        assert ordered_event_ids == event_ids

    def test_list_ordering_descending(self, rf):
        events = factories.EventFactory.create_batch(3)
        events.sort(key=lambda e: e.event_identifier, reverse=True)

        # Order by the Event identifier because the values are globally unique.
        # Pure Python vs the Django ORM sort items with matching keys differently.
        request = rf.get('?orderby=event_identifier&orderdir=descending')
        response = views.app_event(request)
        list_events = objectify.fromstring(response.content.decode('utf-8')).entry
        ordered_event_ids = [f.title for f in list_events]
        event_ids = [f.event_identifier for f in events]

        assert ordered_event_ids == event_ids

    @pytest.mark.xfail(reason="The attribute name is not checked before sorting.")
    def test_list_ordering_with_unknown_attribute_returns_ok(self, rf):
        factories.EventFactory.create_batch(3)
        request = rf.get('?orderby=fake_attribute')
        response = views.app_event(request)
        assert response.status_code == 200

    def test_get_with_identifier_returns_ok(self, rf):
        event = factories.EventFactory.create()
        request = rf.get('/', HTTP_HOST='example.com')
        response = views.app_event(request, event.event_identifier)
        assert response.status_code == 200

    def test_get_with_invalid_identifier_returns_not_found(self, rf):
        request = rf.get('/', HTTP_HOST='example.com')
        response = views.app_event(request, 'ark:/00001/dne')
        assert response.status_code == 404

    def test_get_with_identifier_response_content_type(self, rf):
        event = factories.EventFactory.create()
        request = rf.get('/', HTTP_HOST='example.com')
        response = views.app_event(request, event.event_identifier)
        assert response.get('Content-Type') == self.CONTENT_TYPE

    def test_get_with_identifier_content(self, rf):
        event = factories.EventFactory.create()
        request = rf.get('/', HTTP_HOST='example.com')
        response = views.app_event(request, event.event_identifier)
        assert event.event_identifier in response.content.decode('utf-8')

    def test_delete_returns_ok(self, rf):
        event = factories.EventFactory.create()
        request = rf.delete('/', HTTP_HOST='example.com')
        response = views.app_event(request, event.event_identifier)
        assert response.status_code == 200

    def test_delete_with_invalid_identifier_returns_not_found(self, rf):
        request = rf.delete('/', HTTP_HOST='example.com')
        response = views.app_event(request, 'ark:/00001/dne')
        assert response.status_code == 404

    def test_delete_response_content_type(self, rf):
        event = factories.EventFactory.create()
        request = rf.delete('/', HTTP_HOST='example.com')
        response = views.app_event(request, event.event_identifier)
        assert response.get('Content-Type') == self.CONTENT_TYPE

    def test_delete_response_content(self, rf):
        event = factories.EventFactory.create()
        request = rf.delete('/', HTTP_HOST='example.com')
        response = views.app_event(request, event.event_identifier)
        assert event.event_identifier in response.content.decode('utf-8')

    def test_delete_removes_event(self, rf):
        event = factories.EventFactory.create()
        request = rf.delete('/', HTTP_HOST='example.com')
        views.app_event(request, event.event_identifier)
        assert models.Agent.objects.count() == 0

    def test_head_without_identifier(self, rf):
        request = rf.head('/')
        response = views.app_event(request)
        assert response.content == b'', b'The message body must be empty'
        assert response.status_code == 200

    def test_head_and_get_headers_match_without_identifier(self, rf):
        head_request, get_request = rf.head('/'), rf.get('/')

        head_response = views.app_event(head_request)
        get_response = views.app_event(get_request)

        expected_headers = get_response.serialize_headers()
        actual_headers = head_response.serialize_headers()

        assert expected_headers == actual_headers, 'The response headers do not match.'

    def test_head_with_identifier(self, rf):
        event = factories.EventFactory.create()
        request = rf.head('/')
        response = views.app_event(request, event.event_identifier)
        assert response.content == b'', b'The message body must be empty'
        assert response.status_code == 200

    def test_head_and_get_headers_match_with_identifier(self, rf):
        event = factories.EventFactory.create()

        head_request = rf.head('/', HTTP_HOST='example.com')
        get_request = rf.get('/', HTTP_HOST='example.com')

        head_response = views.app_event(head_request, event.event_identifier)
        get_response = views.app_event(get_request, event.event_identifier)

        expected_headers = get_response.serialize_headers()
        actual_headers = head_response.serialize_headers()

        assert expected_headers == actual_headers, 'The response headers do not match.'


class TestEventSearch:
    """Tests for views.event_search."""
    RESULTS_PER_PAGE = views.EVENT_SEARCH_PER_PAGE

    def response_has_event(self, response, event):
        """True if the event is the only Event in the response context."""
        paginated_entries = response.context['events']
        filtered_entry = paginated_entries[0]

        if not len(paginated_entries) == 1:
            return False

        if not filtered_entry.event_identifier == event.event_identifier:
            return False
        return True

    def response_includes_event(self, response, event):
        events = response.context[-1]['entries'].object_list
        event_ids = [e.event_identifier for e in events]
        return event.event_identifier in event_ids

    def test_returns_ok(self, rf):
        request = rf.get('/')
        response = views.event_search(request)
        assert response.status_code == 200

    def test_results_per_page(self, client):
        factories.EventFactory.create_batch(self.RESULTS_PER_PAGE * 3)

        url = reverse('event-search')
        response = client.get(url)

        context = response.context
        assert len(context['events']) == self.RESULTS_PER_PAGE

    def test_filtering_results(self, client):
        event = factories.EventFactory.create(linking_objects=True)
        linking_object = event.linking_objects.first()

        factories.EventFactory.create_batch(30)

        url = reverse('event-search')
        response = client.get(
            url, {
                'event_outcome': event.event_outcome,
                'event_type': event.event_type,
                'linked_object_id': linking_object.object_identifier
            })

        assert self.response_has_event(response, event)


class TestJsonEventSearch:
    """Tests for views.json_event_search."""
    RESULTS_PER_PAGE = views.EVENT_SEARCH_PER_PAGE
    CONTENT_TYPE = 'application/json'
    REL_SELF = 'self'
    REL_FIRST = 'first'
    REL_LAST = 'last'
    REL_NEXT = 'next'
    REL_PREVIOUS = 'previous'

    def response_has_entry(self, response, event):
        """True if the event is the only Event in the response content."""
        data = json.loads(response.content.decode('utf-8'))
        entries = data['feed']['entry']
        filtered_entry = entries[0]

        if len(entries) != 1:
            return False
        if filtered_entry['identifier'] != event.event_identifier:
            return False
        return True

    def response_includes_event(self, response, event):
        events = json.loads(response.content.decode('utf-8'))['feed']['entry']
        event_ids = [e['identifier'] for e in events]
        return event.event_identifier in event_ids

    def test_returns_ok(self, rf):
        request = rf.get('/')
        response = views.json_event_search(request)
        assert response.status_code == 200

    def test_response_content_type(self, rf):
        request = rf.get('/')
        response = views.json_event_search(request)
        assert response.get('Content-Type') == self.CONTENT_TYPE

    def test_no_results(self, rf):
        """Check the response content when there are no Events
        in the database.
        """
        request = rf.get('/')
        response = views.json_event_search(request)
        data = json.loads(response.content.decode('utf-8'))
        assert data.get('feed') is not None
        assert data.get('feed', {}).get('entry') is not None
        assert not len(data.get('feed', {}).get('entry'))
        assert response.status_code == 200

    def test_results_per_page(self, rf):
        per_page = self.RESULTS_PER_PAGE
        factories.EventFactory.create_batch(per_page*4)
        request = rf.get('/')
        response = views.json_event_search(request)
        data = json.loads(response.content.decode('utf-8'))
        assert len(data['feed']['entry']) == per_page

    def test_opensearch_query(self, rf):
        factories.EventFactory.create_batch(10)
        request = rf.get('/fakefield=true')
        response = views.json_event_search(request)
        data = json.loads(response.content.decode('utf-8'))

        assert data['feed']['opensearch:Query'] == request.GET

    def test_opensearch_itemsPerPage(self, rf):
        factories.EventFactory.create_batch(10)
        request = rf.get('/')
        response = views.json_event_search(request)
        data = json.loads(response.content.decode('utf-8'))

        assert data['feed']['opensearch:itemsPerPage'] == self.RESULTS_PER_PAGE

    def test_opensearch_startIndex(self, rf):
        factories.EventFactory.create_batch(10)
        request = rf.get('/')
        response = views.json_event_search(request)
        data = json.loads(response.content.decode('utf-8'))

        assert data['feed']['opensearch:startIndex'] == '1'

    def test_opensearch_totalResults(self, rf):
        num_events = 100
        factories.EventFactory.create_batch(num_events)
        request = rf.get('/')
        response = views.json_event_search(request)
        data = json.loads(response.content.decode('utf-8'))

        assert data['feed']['opensearch:totalResults'] == num_events

    def test_pagination_links(self, rf):
        num_events = self.RESULTS_PER_PAGE * 3
        factories.EventFactory.create_batch(num_events)
        request = rf.get('/?page=2')
        response = views.json_event_search(request)
        data = json.loads(response.content.decode('utf-8'))

        assert len(data['feed']['link']) == 5

        for link in data['feed']['link']:
            if link['rel'] == self.REL_SELF:
                assert 'page=2' in link['href']
            elif link['rel'] == self.REL_PREVIOUS:
                assert 'page=1' in link['href']
            elif link['rel'] == self.REL_FIRST:
                assert 'page=1' in link['href']
            elif link['rel'] == self.REL_NEXT:
                assert 'page=3' in link['href']
            elif link['rel'] == self.REL_LAST:
                assert 'page=3' in link['href']

    def test_filter_by_start_date(self, rf):
        datetime_obj = datetime.now().replace(2015, 1, 1)
        factories.EventFactory.create_batch(30, event_date_time=datetime_obj)
        event = factories.EventFactory.create(event_date_time=datetime.now())

        request = rf.get('/?start_date=01/31/2015')
        response = views.json_event_search(request)

        assert self.response_has_entry(response, event)

    def test_filter_by_end_date(self, rf):
        datetime_obj = datetime.now().replace(2015, 1, 1)
        factories.EventFactory.create_batch(30, event_date_time=datetime.now())
        event = factories.EventFactory.create(event_date_time=datetime_obj)

        request = rf.get('/?end_date=01/31/2015')
        response = views.json_event_search(request)

        assert self.response_has_entry(response, event)

    @pytest.mark.xfail(reason='Magic strings prevent block from executing.')
    def test_filter_by_linking_object_id(self, rf):
        factories.EventFactory.create_batch(30)
        event = factories.EventFactory.create(linking_objects=True)
        linking_object = event.linking_objects.first()

        url = '/?linked_object_id={0}'.format(linking_object.object_identifier)
        request = rf.get(url)
        response = views.json_event_search(request)

        assert self.response_has_entry(response, event)

    def test_filter_by_outcome(self, rf):
        event_outcome = random.choice(EVENT_OUTCOME_CHOICES)[0]
        factories.EventFactory.create_batch(10)
        event = factories.EventFactory.create(event_outcome=event_outcome)

        request = rf.get('/?event_outcome={0}'.format(urlquote(event_outcome)))
        response = views.json_event_search(request)

        assert self.response_includes_event(response, event)

    def test_filter_by_event_type(self, rf):
        event_type = random.choice(EVENT_TYPE_CHOICES)[0]
        factories.EventFactory.create_batch(10)
        event = factories.EventFactory.create(event_type=event_type)

        request = rf.get('/?event_type={0}'.format(urlquote(event_type)))
        response = views.json_event_search(request)

        assert self.response_includes_event(response, event)
