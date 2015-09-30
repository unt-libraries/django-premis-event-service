import uuid

import factory
import factory.fuzzy

from django.utils import timezone

from premis_event_service import models


UUID_TYPE = 'http://purl.org/net/untl/vocabularies/identifier-qualifiers/#UUID'

URL_TYPE = 'http://purl.org/net/untl/vocabularies/identifier-qualifiers/#UUID'

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
    def linking_objects(self, create, extracted, **kwargs):
        """Post generation hook to add related LinkObject instances.

        Pass `linking_objects=True` to the create function to activate.
        """
        if create and extracted:
            linking_objects = LinkObjectFactory.create_batch(2)
            self.linking_objects.add(*linking_objects)
