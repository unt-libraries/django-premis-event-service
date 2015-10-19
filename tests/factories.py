import uuid

import factory
import factory.fuzzy

from django.utils import timezone

from premis_event_service import models


UUID_TYPE = 'http://purl.org/net/untl/vocabularies/identifier-qualifiers/#UUID'

URL_TYPE = 'http://purl.org/net/untl/vocabularies/identifier-qualifiers/#URL'

EVENT_TYPES = [
    'http://purl.org/net/untl/vocabularies/preservationEvents/#replication',
    'http://purl.org/net/untl/vocabularies/preservationEvents/#fixityCheck'
]

EVENT_OUTCOMES = [
    'http://purl.org/net/untl/vocabularies/eventOutcomes/#success',
    'http://purl.org/net/untl/vocabularies/eventOutcomes/#failure'
]

AGENTS = [
    'http://example.com/agent/codareplicationverification',
    'http://example.com/agent/codavalidation',
]


class AgentFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.Agent

    agent_identifier = factory.fuzzy.FuzzyText()
    agent_name = factory.fuzzy.FuzzyText()
    agent_type = factory.fuzzy.FuzzyChoice(v for k, v in models.AGENT_TYPE_CHOICES)
    agent_note = factory.fuzzy.FuzzyText()


class AgentXML(object):

    def __init__(self, agent):
        self.agent = agent

    @property
    def xml(self):
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
        return xml.format(**vars(self.agent))


class LinkObjectFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.LinkObject

    object_identifier = factory.Sequence(lambda n: 'ark:/00001/coda{0}'.format(n))
    object_type = 'http://purl.org/net/untl/vocabularies/identifier-qualifiers/#ARK'
    object_role = None


class EventFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.Event

    event_identifier = factory.Sequence(lambda n: str(uuid.uuid4()))
    event_identifier_type = UUID_TYPE

    event_type = factory.fuzzy.FuzzyChoice(EVENT_TYPES)
    event_date_time = factory.fuzzy.FuzzyDateTime(timezone.now())
    event_detail = factory.fuzzy.FuzzyText()
    event_outcome = factory.fuzzy.FuzzyChoice(EVENT_OUTCOMES)
    event_outcome_detail = factory.fuzzy.FuzzyText()

    linking_agent_identifier_type = URL_TYPE
    linking_agent_identifier_value = factory.fuzzy.FuzzyChoice(AGENTS)
    linking_agent_role = ''

    @factory.post_generation
    def linking_objects(self, create, extracted, count=1, **kwargs):
        """Post generation hook to add related LinkObject instances.

        Pass `linking_objects=True` to the create function to activate.
        """
        if create and extracted:
            linking_objects = LinkObjectFactory.create_batch(count)
            self.linking_objects.add(*linking_objects)


class EventXML(object):

    def __init__(self, event):
        self.event = event

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
                **vars(self.event))

    @property
    def xml(self):
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
                **vars(self.event))

    def _linking_objects_xml(self):
        template = """<premis:linkingObjectIdentifier>
            <premis:linkingObjectIdentifierType>{object_type}</premis:linkingObjectIdentifierType>
            <premis:linkingObjectIdentifierValue>{object_identifier}</premis:linkingObjectIdentifierValue>
            <premis:linkingObjectRole>{object_role}</premis:linkingObjectRole>
        </premis:linkingObjectIdentifier>
        """
        xml = ''
        for obj in self.event.linking_objects.all():
            xml += template.format(**vars(obj))
        return xml
