import uuid

import factory
import factory.fuzzy

from datetime import datetime

from premis_event_service import models
from premis_event_service.config.settings import base as settings


UUID_TYPE = 'http://purl.org/net/untl/vocabularies/identifier-qualifiers/#UUID'

URL_TYPE = 'http://purl.org/net/untl/vocabularies/identifier-qualifiers/#URL'

EVENT_TYPES = [value for value, _ in settings.EVENT_TYPE_CHOICES]

EVENT_OUTCOMES = [value for value, _ in settings.EVENT_OUTCOME_CHOICES]

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
    event_date_time = factory.fuzzy.FuzzyNaiveDateTime(datetime.now())
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
