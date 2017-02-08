'''
Default values for various app-defined settings

Formula: FOO = getattr(settings, 'FOO', "default_value")

These settings values will be used only if they are not found in the project
settings.py module. If you want to override any of these values, just redefine
them in that file rather than here.
'''
from django.conf import settings

# Used in codalib/util.py
EVENT_ID_TYPE_XML = getattr(
    settings, 'EVENT_ID_TYPE_XML',
    "http://purl.org/net/untl/vocabularies/identifier-qualifiers/#UUID"
)
LINK_AGENT_ID_TYPE_XML = getattr(
    settings, 'LINK_AGENT_ID_TYPE_XML',
    "http://purl.org/net/untl/vocabularies/identifier-qualifiers/#URL"
)
LINK_AGENT_ID_ROLE_XML = getattr(
    settings, 'LINK_AGENT_ID_ROLE_XML',
    "http://id.loc.gov/vocabulary/preservation/eventRelatedAgentRole/exe"
)

# Used in codalib/bagatom.py
BAGATOM_BAG_NAMESPACE = getattr(
    settings, 'BAGATOM_BAG_NAMESPACE', "TODO"
)
BAGATOM_QXML_NAMESPACE = getattr(
    settings, 'BAGATOM_QXML_NAMESPACE', "TODO"
)
BAGATOM_NODE_NAMESPACE = getattr(
    settings, 'BAGATOM_NODE_NAMESPACE', "TODO"
)

# Used in forms.py
EVENT_OUTCOME_CHOICES = getattr(
    settings, 'EVENT_OUTCOME_CHOICES',
    (
        ('', 'None'),
        ('http://purl.org/net/untl/vocabularies/eventOutcomes/#success', 'Success'),
        ('http://purl.org/net/untl/vocabularies/eventOutcomes/#failure', 'Failure'),
    )
)
EVENT_TYPE_CHOICES = getattr(
    settings, 'EVENT_TYPE_CHOICES',
    (
        ('', 'None'),
        ('http://id.loc.gov/vocabulary/preservation/eventType/fix', 'Fixity Check'),
        ('http://id.loc.gov/vocabulary/preservation/eventType/rep', 'Replication'),
        ('http://id.loc.gov/vocabulary/preservation/eventType/ing', 'Ingestion'),
        ('http://id.loc.gov/vocabulary/preservation/eventType/mig', 'Migration'),
    )
)

# Archival Resource Key Name Assigning Authority Number:
# http://www.cdlib.org/services/uc3/naan_table.html
ARK_NAAN = getattr(settings, 'ARK_NAAN', 67531)
