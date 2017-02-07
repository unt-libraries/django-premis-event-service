from django.core.urlresolvers import reverse
from django.db import models


# construct choices for the agent type
AGENT_TYPE_CHOICES = [
    ('Personal', 'Personal'),
    ('Organization', 'Organization'),
    ('Event', 'Event'),
    ('Software', 'Software'),
]


class Agent(models.Model):
    """
    Structure for the half a dozen or so Agents we have in the system.
    """

    agent_identifier = models.CharField(
        unique=True,
        max_length=255,
        help_text="Short identifier for agent to be used in url.",
        db_index=True,
    )
    agent_name = models.CharField(
        max_length=255,
        help_text="Name of agent."
    )
    agent_type = models.CharField(
        max_length=13,
        choices=AGENT_TYPE_CHOICES,
        help_text="A high-level characterization of the type of agent."
    )
    agent_note = models.TextField(
        blank=True,
        help_text="Optional note about agent."
    )

    def __unicode__(self):
        return self.agent_name

    def get_absolute_url(self):
        return reverse('agent-detail', args=[self.agent_identifier])

    class Meta:
        ordering = ['agent_name']


class LinkObject(models.Model):
    """
    A link object is the bag that is tied to an event.
    """

    object_identifier = models.CharField(
        max_length=255,
        help_text="Unique identifier for this object.",
        primary_key=True
    )
    object_type = models.CharField(
        max_length=255,
        help_text="High-level characterization of the type of object \
            identifier."
    )
    object_role = models.CharField(
        max_length=255,
        help_text="A high-level characterization of the role of the object.",
        null=True
    )

    def __unicode__(self):
        return self.object_identifier


class EventManager(models.Manager):

    def search(self, **kwargs):
        """Filter the Events based on
           - A start_date less than an event_date_time
           - An end_date greater than an event_date_time
           - An event_outcome
           - An event_type
           - A related LinkObject.object_identifier

        Arguments:
            start_date (optional) - datetime
            end_date (optional) - datetime
            event_outcome (optional) - string
            event_type (optional) - string
            linked_object_id (optional) - string
        """
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')
        outcome = kwargs.get('event_outcome')
        event_type = kwargs.get('event_type')
        linked_object_id = kwargs.get('linked_object_id')

        events = self.get_queryset().order_by('-event_date_time')

        # Filter based on the supplied the arguments.
        events = events.filter(event_date_time__gte=start_date) if start_date else events
        events = events.filter(event_date_time__lte=end_date) if end_date else events
        events = events.filter(event_outcome=outcome) if outcome else events
        events = events.filter(event_type=event_type) if event_type else events

        if linked_object_id:
            events = events.filter(linking_objects__object_identifier=linked_object_id)

        return events


class Event(models.Model):
    """
    Holds all data for the events, along with the linking objects ids
    """

    objects = EventManager()

    help_text = "Unique identifier for an event. example: " +\
        "urn:uuid:12345678-1234-5678-1234-567812345678"
    event_identifier = models.CharField(
        primary_key=True,
        max_length=64,
        editable=False,
        help_text=help_text
    )
    event_identifier_type = models.CharField(
        max_length=255,
        help_text="The categorization of the nature of the identifier used."
    )
    help_text = "A categorization of the nature of the event use " +\
        "controlled vocabulary."
    event_type = models.CharField(
        max_length=255,
        help_text=help_text,
        db_index=True
    )
    event_date_time = models.DateTimeField(
        help_text="Date/Time event was completed.",
        db_index=True
    )
    event_added = models.DateTimeField(
        auto_now=True,
        help_text="Date/Time event was added to system.",
        db_index=True
    )
    event_detail = models.TextField(
        blank=True,
        help_text="Additional information about the event."
    )
    help_text = "A categorization of the overall result of the event in " + \
        "terms of success, partial success, or failure."
    event_outcome = models.CharField(
        max_length=255,
        help_text=help_text,
        db_index=True
    )
    help_text = "A non-coded detailed description of the result " + \
        "of the event."
    event_outcome_detail = models.TextField(
        blank=True,
        help_text=help_text
    )
    help_text = "A designation of the domain in which the linking agent." + \
        " identifier is unique."
    linking_agent_identifier_type = models.CharField(
        max_length=255,
        help_text=help_text
    )
    linking_agent_identifier_value = models.CharField(
        max_length=255,
        help_text="The value of the linking agent identifier.",
        db_index=True
    )
    linking_agent_role = models.CharField(
        max_length=255,
        help_text="The role of the agent in relation to this event."
    )
    linking_objects = models.ManyToManyField(LinkObject)

    def __unicode__(self):
        return self.event_identifier

    class Meta:
        ordering = ["event_added"]

    def link_objects_string(self):
        values = self.linking_objects.values()
        idList = []
        for value in values:
            idList.append(value["object_identifier"])
        return "\n".join(idList)

    def is_good(self):
        if self.event_outcome.endswith("#success") or \
                self.event_outcome == "pass":
            return True
        return False

    is_good.short_description = "Pass?"
    is_good.boolean = True
