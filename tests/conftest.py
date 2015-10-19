import pytest

from . import factories


@pytest.fixture
def event_xml():
    event = factories.EventFactory.create(linking_objects=True)
    return factories.EventXML(event)


@pytest.fixture
def agent_xml():
    agent = factories.AgentFactory.build()
    return factories.AgentXML(agent)
