'''
Default values for various app-defined settings

Formula: FOO = getattr(settings, 'FOO', "default_value")

(default_value is used if the setting is not found in the project's settings.py)
'''
from django.conf import settings

# Used in coda/util.py
EVENT_ID_TYPE_XML = getattr(settings, 'EVENT_ID_TYPE_XML', "TODO")
LINK_AGENT_ID_TYPE_XML = getattr(settings, 'LINK_AGENT_ID_TYPE_XML', "TODO")
LINK_AGENT_ID_ROLE_XML = getattr(settings, 'LINK_AGENT_ID_ROLE_XML', "TODO")

# Used in coda/bagatom.py
BAGATOM_BAG_NAMESPACE = getattr(settings, 'BAGATOM_BAG_NAMESPACE', "TODO")
BAGATOM_QXML_NAMESPACE = getattr(settings, 'BAGATOM_QXML_NAMESPACE', "TODO")
BAGATOM_NODE_NAMESPACE = getattr(settings, 'BAGATOM_NODE_NAMESPACE', "TODO")

# Used in forms.py
EVENT_OUTCOME_CHOICES = getattr(settings, 'EVENT_OUTCOME_CHOICES',
    (
        ('', 'None'),
        ('TODO', 'Success'),
        ('TODO', 'Failure'),
    )
)
EVENT_TYPE_CHOICES = getattr(settings, 'EVENT_TYPE_CHOICES',
    (
        ('', 'None'),
        ('TODO', 'Fixity Check'),
        ('TODO', 'Replication'),
        ('TODO', 'Ingestion'),
        ('TODO', 'Migration'),
    )
)

