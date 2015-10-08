import json

from lxml import objectify
import pytest

from django.core.urlresolvers import reverse
from django.http import Http404
from django.utils import timezone

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
    event = factories.EventFactory.create()
    request = rf.get('/')
    response = views.humanEvent(request, event.event_identifier)
    assert response.status_code == 200


def test_humanAgent_with_invalid_identifier(rf):
    request = rf.get('/')
    response = views.humanAgent(request, 'test-identifier')
    assert response.status_code == 200


def test_humanAgent_returns_all_agents(client):
    factories.AgentFactory.create_batch(30)
    response = client.get(
            reverse('premis_event_service.views.humanAgent'))
    view_context = response.context[-1]
    assert len(view_context['agents']) == models.Agent.objects.count()


def test_humanAgent_with_identifier(client):
    agent = factories.AgentFactory.create()
    response = client.get(
            reverse('premis_event_service.views.humanAgent', args=[agent.agent_identifier]))
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
    response = client.get(reverse('premis_event_service.views.recent_event_list'))

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
    """Verify that the json output has matches the Agent attributes."""
    agent = factories.AgentFactory.create()
    request = rf.get('/')
    response = views.json_agent(request, agent.agent_identifier)
    payload = json.loads(response.content)

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
    assert "So you would like XML for the event with identifier" in response.content


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

    @pytest.fixture
    def app_agent_xml(self):
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

    def test_post_returns_created(self, rf, app_agent_xml):
        _, xml = app_agent_xml
        request = rf.post('/', xml, content_type='application/xml')
        response = views.app_agent(request)
        assert response.status_code == 201

    def test_post_response_content_type(self, rf, app_agent_xml):
        _, xml = app_agent_xml
        request = rf.post('/', xml, content_type='application/xml')
        response = views.app_agent(request)
        assert response.get('Content-Type') == self.CONTENT_TYPE

    def test_post_response_content(self, rf, app_agent_xml):
        identifier, xml = app_agent_xml
        request = rf.post('/', xml, content_type='application/xml')
        response = views.app_agent(request)
        assert identifier in response.content

    @pytest.mark.xfail(reason='POST request without body raises uncaught exception.')
    def test_post_without_body_is_handled(self, rf):
        request = rf.post('/')
        views.app_agent(request)

    def test_returns_bad_request(self, rf):
        """Check that a request that is not GET, POST, PUT, or DELETE will
        result in a response with status code 400.
        """
        request = rf.head('/')
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

    def test_put_returns_ok(self, app_agent_xml, rf):
        identifier, xml = app_agent_xml
        agent = factories.AgentFactory.create(agent_identifier=identifier)

        request = rf.put('/', xml, content_type='application/xml')
        response = views.app_agent(request, agent.agent_identifier)
        assert response.status_code == 200

    def test_put_response_content_type(self, app_agent_xml, rf):
        identifier, xml = app_agent_xml
        agent = factories.AgentFactory.create(agent_identifier=identifier)

        request = rf.put('/', xml, content_type='application/xml')
        response = views.app_agent(request, agent.agent_identifier)
        assert response.get('Content-Type') == self.CONTENT_TYPE

    def test_put_agent_updated(self, app_agent_xml, rf):
        identifier, xml = app_agent_xml
        agent = factories.AgentFactory.create(agent_identifier=identifier)

        request = rf.put('/', xml, content_type='application/xml')
        views.app_agent(request, agent.agent_identifier)

        updated_agent = models.Agent.objects.get(agent_identifier=identifier)
        assert updated_agent.agent_name != agent.agent_name

    def test_put_response_content(self, app_agent_xml, rf):
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

    def test_get_with_identifier_response_content_type(self, rf):
        agent = factories.AgentFactory.create()
        request = rf.get('/')
        response = views.app_agent(request, agent.agent_identifier)
        assert response.get('Content-Type') == self.CONTENT_TYPE

    def test_get_with_identifier_response_content(self, rf):
        agent = factories.AgentFactory.create()
        request = rf.get('/')
        response = views.app_agent(request, agent.agent_identifier)
        assert agent.agent_identifier in response.content


class TestAppEvent:
    """Tests for views.app_event."""
    CONTENT_TYPE = 'application/atom+xml'
    RESULTS_PER_PAGE = 20

    def event_in_filtered_results(self, response, event):
        """True if the event is the only event in the response content."""
        xml = objectify.fromstring(response.content)
        if len(xml.entry) != 1:
            return False
        if event.event_identifier not in response.content:
            return False
        return True

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
        assert response.get('Content-Type') == self.CONTENT_TYPE

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
        xml = objectify.fromstring(response.content)

        assert len(xml.entry) == self.RESULTS_PER_PAGE

    @pytest.mark.xfail(reason='Global name DATE_FORMAT is not defined.')
    def test_list_filtering_by_start_date(self, rf):
        datetime_obj = timezone.now().replace(2015, 1, 1)
        factories.EventFactory.create_batch(30, event_date_time=datetime_obj)
        event = factories.EventFactory.create(event_date_time=timezone.now())

        request = rf.get('/?start_date=01/31/2015')
        response = views.app_event(request)
        assert self.event_in_filtered_results(response, event)

    @pytest.mark.xfail(reason='Global name DATE_FORMAT is not defined.')
    def test_list_filtering_by_end_date(self, rf):
        datetime_obj = timezone.now().replace(2015, 1, 1)
        factories.EventFactory.create_batch(30, event_date_time=timezone.now())
        event = factories.EventFactory.create(event_date_time=datetime_obj)

        request = rf.get('/?end_date=01/31/2015')
        response = views.app_event(request)
        assert self.event_in_filtered_results(response, event)

    def test_list_filtering_by_linking_object_id(self, rf):
        factories.EventFactory.create_batch(30)
        event = factories.EventFactory.create(linking_objects=True)
        linking_object = event.linking_objects.first()

        url = '/?link_object_id={0}'.format(linking_object.object_identifier)
        request = rf.get(url)
        response = views.app_event(request)

        assert self.event_in_filtered_results(response, event)

    def test_list_filtering_by_event_outcome(self, rf):
        factories.EventFactory.create_batch(30)

        event_outcome = 'success'
        event = factories.EventFactory.create(event_outcome=event_outcome)

        request = rf.get('?outcome={0}'.format(event_outcome))
        response = views.app_event(request)
        assert self.event_in_filtered_results(response, event)

    def test_list_filtering_by_event_type(self, rf):
        factories.EventFactory.create_batch(30)

        event_type = 'Test Type'
        event = factories.EventFactory.create(event_type=event_type)

        request = rf.get('?type={0}'.format(event_type))
        response = views.app_event(request)
        assert self.event_in_filtered_results(response, event)

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
        assert event.event_identifier in response.content

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
        assert event.event_identifier in response.content

    def test_delete_removes_event(self, rf):
        event = factories.EventFactory.create()
        request = rf.delete('/', HTTP_HOST='example.com')
        views.app_event(request, event.event_identifier)
        assert models.Agent.objects.count() == 0


class TestEventSearch:
    """Tests for views.event_search."""
    RESULTS_PER_PAGE = 20

    def response_has_event(self, response, event):
        """True event is the only Event in the response context."""
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

    def test_results_per_page(self, client):
        factories.EventFactory.create_batch(self.RESULTS_PER_PAGE * 3)

        url = reverse('premis_event_service.views.event_search')
        response = client.get(url)

        context = response.context[-1]
        assert len(context['entries']) == self.RESULTS_PER_PAGE

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

    @pytest.mark.xfail(reason='Magic strings prevent block from executing.')
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


class TestJsonEventSearch:
    """Tests for views.json_event_search."""
    RESULTS_PER_PAGE = 20
    CONTENT_TYPE = 'application/json'
    REL_SELF = 'self'
    REL_FIRST = 'first'
    REL_LAST = 'last'
    REL_NEXT = 'next'
    REL_PREVIOUS = 'previous'

    def response_has_entry(self, response, event):
        """True event is the only Event in the response content."""
        data = json.loads(response.content)
        entries = data['feed']['entry']
        filtered_entry = entries[0]

        if len(entries) != 1:
            return False
        if filtered_entry['identifier'] != event.event_identifier:
            return False
        return True

    def test_returns_ok(self, rf):
        request = rf.get('/')
        response = views.json_event_search(request)
        assert response.status_code == 200

    def test_response_content_type(self, rf):
        request = rf.get('/')
        response = views.json_event_search(request)
        assert response.get('Content-Type') == self.CONTENT_TYPE

    def test_no_results(self, rf):
        """Check that response content when there are no Events
        in the database.
        """
        request = rf.get('/')
        response = views.json_event_search(request)
        data = json.loads(response.content)
        assert len(data) == 0
        assert response.status_code == 200

    def test_results_per_page(self, rf):
        factories.EventFactory.create_batch(30)
        request = rf.get('/')
        response = views.json_event_search(request)
        data = json.loads(response.content)
        assert len(data['feed']['entry']) == self.RESULTS_PER_PAGE

    def test_opensearch_query(self, rf):
        factories.EventFactory.create_batch(10)
        request = rf.get('/fakefield=true')
        response = views.json_event_search(request)
        data = json.loads(response.content)

        assert data['feed']['opensearch:Query'] == request.GET

    def test_opensearch_itemsPerPage(self, rf):
        factories.EventFactory.create_batch(10)
        request = rf.get('/')
        response = views.json_event_search(request)
        data = json.loads(response.content)

        assert data['feed']['opensearch:itemsPerPage'] == self.RESULTS_PER_PAGE

    def test_opensearch_startIndex(self, rf):
        factories.EventFactory.create_batch(10)
        request = rf.get('/')
        response = views.json_event_search(request)
        data = json.loads(response.content)

        assert data['feed']['opensearch:startIndex'] == '1'

    def test_opensearch_totalResults(self, rf):
        num_events = 100
        factories.EventFactory.create_batch(num_events)
        request = rf.get('/')
        response = views.json_event_search(request)
        data = json.loads(response.content)

        assert data['feed']['opensearch:totalResults'] == num_events

    def test_pagination_links(self, rf):
        num_events = self.RESULTS_PER_PAGE * 3
        factories.EventFactory.create_batch(num_events)
        request = rf.get('/?page=2')
        response = views.json_event_search(request)
        data = json.loads(response.content)

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
        datetime_obj = timezone.now().replace(2015, 1, 1)
        factories.EventFactory.create_batch(30, event_date_time=datetime_obj)
        event = factories.EventFactory.create(event_date_time=timezone.now())

        request = rf.get('/?start_date=01/31/2015')
        response = views.json_event_search(request)

        assert self.response_has_entry(response, event)

    def test_filter_by_end_date(self, rf):
        datetime_obj = timezone.now().replace(2015, 1, 1)
        factories.EventFactory.create_batch(30, event_date_time=timezone.now())
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
        event_outcome = 'Test outcome'
        factories.EventFactory.create_batch(30)
        event = factories.EventFactory.create(event_outcome=event_outcome)

        request = rf.get('/?outcome={0}'.format(event_outcome))
        response = views.json_event_search(request)

        assert self.response_has_entry(response, event)

    def test_filter_by_event_type(self, rf):
        event_type = 'Test Event Type'
        factories.EventFactory.create_batch(30)
        event = factories.EventFactory.create(event_type=event_type)

        request = rf.get('/?type={0}'.format(event_type))
        response = views.json_event_search(request)

        assert self.response_has_entry(response, event)
