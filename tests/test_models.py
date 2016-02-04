import pytest

from django.utils import timezone
from . import factories
from premis_event_service import models


class TestAgent:

    def test_unicode(self):
        agent = factories.AgentFactory.build()
        assert agent.agent_name == unicode(agent)

    def test_get_absolute_url(self):
        agent = factories.AgentFactory.build()
        url = '/agent/{0}/'.format(agent.agent_identifier)
        assert agent.get_absolute_url() == url


class TestLinkObject:

    def test_unicode(self):
        link_object = factories.LinkObjectFactory.build()
        assert link_object.object_identifier == unicode(link_object)


class TestEvent:

    def test_unicode(self):
        event = factories.EventFactory.build()
        assert event.event_identifier == unicode(event)

    @pytest.mark.django_db
    def test_link_objects_string_with_link_objects(self):
        event = factories.EventFactory.create(
            linking_objects=True,
            linking_objects__count=2)

        linking_objects = event.linking_objects.all()
        string = '\n'.join([s.object_identifier for s in linking_objects])
        assert string == event.link_objects_string()

    @pytest.mark.django_db
    def test_link_objects_string_without_link_objects(self):
        event = factories.EventFactory.build()
        assert '' == event.link_objects_string()

    def test_is_good_is_true(self):
        event = factories.EventFactory.build(
            event_outcome='http://example.com/#success')

        assert event.is_good() is True

    def test_is_good_is_false(self):
        event = factories.EventFactory.build(
            event_outcome='http://example.com/#not-success')

        assert event.is_good() is False


@pytest.mark.django_db
class TestEventManager:

    def results_has_event(self, results, event):
        """True if the event is the only Event in the response context."""
        if not len(results) == 1:
            return False

        result = results[0]
        if not result.event_identifier == event.event_identifier:
            return False
        return True

    @pytest.fixture
    def manager(self):
        """Fixture to provide the EventManager object with the
        correct setup.
        """
        manager = models.EventManager()
        manager.model = models.Event
        return manager

    def test_search_filters_by_start_date(self, manager):
        event = factories.EventFactory.create(event_date_time=timezone.now())

        # Create a batch of events that occur before the intial event.
        event_date_time = timezone.now().replace(2015, 1, 1)
        factories.EventFactory.create_batch(30, event_date_time=event_date_time)

        # Search for events AFTER the initial event.
        start_date = timezone.now().replace(2015, 1, 2)
        results = manager.search(start_date=start_date)

        assert self.results_has_event(results, event)

    def test_search_filters_by_end_date(self, manager):
        event_date_time = timezone.now().replace(2015, 1, 1)
        event = factories.EventFactory.create(event_date_time=event_date_time)

        # Create a batch of events that occur AFTER the intial event.
        factories.EventFactory.create_batch(30, event_date_time=timezone.now())

        # Search for events from BEFORE this test was executed.
        end_date = timezone.now().replace(2015, 1, 31)
        results = manager.search(end_date=end_date)

        assert self.results_has_event(results, event)

    def test_search_filters_linked_object_id(self, manager):
        factories.EventFactory.create_batch(30)
        event = factories.EventFactory.create(linking_objects=True)
        linking_object = event.linking_objects.first()

        results = manager.search(linked_object_id=linking_object.object_identifier)

        assert self.results_has_event(results, event)

    def test_search_filters_by_event_outcome(self, manager):
        event_outcome = 'Test Outcome'

        factories.EventFactory.create_batch(30)
        event = factories.EventFactory.create(event_outcome=event_outcome)

        results = manager.search(event_outcome=event_outcome)

        assert self.results_has_event(results, event)

    def test_search_filters_by_event_type(self, manager):
        event_type = 'Test Type'

        factories.EventFactory.create_batch(10)
        event = factories.EventFactory.create(event_type=event_type)

        results = manager.search(event_type=event_type)

        assert self.results_has_event(results, event)
