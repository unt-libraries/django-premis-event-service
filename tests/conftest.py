import pytest

from . import factories


class EventTestXML(object):

    def __init__(self):
        self.attributes = factories.EventFactory.attributes()
        self.identifier = self.attributes['event_identifier']
        self._link_object_attributes = factories.LinkObjectFactory.attributes()

    @property
    def entry_xml(self):
        xml = """<?xml version="1.0"?>
            <entry xmlns="http://www.w3.org/2005/Atom">
              <title>{event_identifier}</title>
              <id>http://example.com/APP/event/{event_identifier}/</id>
              <updated>2015-10-02T19:59:22Z</updated>
              <content type="application/xml">
                <premis:event xmlns:premis="info:lc/xmlns/premis-v2">
                  <premis:eventDetail>{event_detail}</premis:eventDetail>
                  <premis:eventOutcomeInformation>
                    <premis:eventOutcomeDetail>{event_outcome_detail}</premis:eventOutcomeDetail>
                    <premis:eventOutcome>{event_outcome}</premis:eventOutcome>
                  </premis:eventOutcomeInformation>
                  <premis:eventType>{event_type}</premis:eventType>
                  <premis:linkingAgentIdentifier>
                    <premis:linkingAgentIdentifierValue>{linking_agent_identifier_value}</premis:linkingAgentIdentifierValue>
                    <premis:linkingAgentIdentifierType>{linking_agent_identifier_type}</premis:linkingAgentIdentifierType>
                  </premis:linkingAgentIdentifier>
                  <premis:eventIdentifier>
                      <premis:eventIdentifierValue>{event_identifier}</premis:eventIdentifierValue>
                    <premis:eventIdentifierType>{event_identifier_type}</premis:eventIdentifierType>
                  </premis:eventIdentifier>
                  <premis:eventDateTime>{event_date_time}</premis:eventDateTime>
                  {linking_objects}
                </premis:event>
              </content>
            </entry>
        """
        return xml.format(
                linking_objects=self._linking_objects_xml(),
                **self.attributes)

    @property
    def obj_xml(self):
        xml = """<?xml version="1.0"?>
            <premis:event xmlns:premis="info:lc/xmlns/premis-v2">
              <premis:eventDetail>{event_detail}</premis:eventDetail>
              <premis:eventOutcomeInformation>
                <premis:eventOutcomeDetail>{event_outcome_detail}</premis:eventOutcomeDetail>
                <premis:eventOutcome>{event_outcome}</premis:eventOutcome>
              </premis:eventOutcomeInformation>
              <premis:eventType>{event_type}</premis:eventType>
              <premis:linkingAgentIdentifier>
                <premis:linkingAgentIdentifierValue>{linking_agent_identifier_value}</premis:linkingAgentIdentifierValue>
                <premis:linkingAgentIdentifierType>{linking_agent_identifier_type}</premis:linkingAgentIdentifierType>
              </premis:linkingAgentIdentifier>
              <premis:eventIdentifier>
                  <premis:eventIdentifierValue>{event_identifier}</premis:eventIdentifierValue>
                <premis:eventIdentifierType>{event_identifier_type}</premis:eventIdentifierType>
              </premis:eventIdentifier>
              <premis:eventDateTime>{event_date_time}</premis:eventDateTime>
              {linking_objects}
            </premis:event>
        """
        return xml.format(
                linking_objects=self._linking_objects_xml(),
                **self.attributes)

    def _linking_objects_xml(self):
        template = """<premis:linkingObjectIdentifier>
            <premis:linkingObjectIdentifierType>{object_type}</premis:linkingObjectIdentifierType>
            <premis:linkingObjectIdentifierValue>{object_identifier}</premis:linkingObjectIdentifierValue>
            <premis:linkingObjectRole>{object_role}</premis:linkingObjectRole>
        </premis:linkingObjectIdentifier>
        """
        return template.format(**self._link_object_attributes)


class AgentTestXML(object):

    def __init__(self):
        self.attributes = factories.AgentFactory.attributes()
        self.identifier = self.attributes['agent_identifier']

    @property
    def obj_xml(self):
        xml = """<?xml version="1.0"?>
            <premis:agent xmlns:premis="info:lc/xmlns/premis-v2">
              <premis:agentIdentifier>
                <premis:agentIdentifierValue>{agent_identifier}</premis:agentIdentifierValue>
                <premis:agentIdentifierType>PES:Agent</premis:agentIdentifierType>
              </premis:agentIdentifier>
              <premis:agentName>{agent_name}</premis:agentName>
              <premis:agentType>{agent_type}</premis:agentType>
              <premis:agentNote>{agent_note}</premis:agentNote>
            </premis:agent>
        """
        return xml.format(**self.attributes)


@pytest.fixture
def event_xml():
    return EventTestXML()


@pytest.fixture
def agent_xml():
    return AgentTestXML()