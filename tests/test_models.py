import pytest

from django.core.urlresolvers import reverse
from . import factories


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
