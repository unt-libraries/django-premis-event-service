=============
Configuration
=============

All configuration related to the PREMIS Event Service takes place inside your 
project's ``settings.py`` file.

Note: Make sure you only make changes in your project's ``settings.py``, not 
the ``settings.py`` file inside the ``premis_event_service`` app directory.

.. contents::
    :local:
    :depth: 2

Mandatory Configuration
-----------------------

1. Update your INSTALLED_APPS setting as follows::

    INSTALLED_APPS = (
        ...
        'django.contrib.humanize',
        'premis_event_service',
    )

2. Make sure you have a TEMPLATE_CONTEXT_PROCESSORS setting defined containing 
   at least the entries shown below::

    TEMPLATE_CONTEXT_PROCESSORS = (
        'django.contrib.auth.context_processors.auth',
        'django.core.context_processors.debug',
        'django.core.context_processors.i18n',
        'django.core.context_processors.media',
        'django.core.context_processors.request',
    )

3. Add a MAINTENANCE_MSG setting at the bottom of the file::

    MAINTENANCE_MSG = ''  # Message to show during maintenance

Customizing the Controlled Vocabulary
-------------------------------------

TODO: General info about controlled event/agent vocabularies

TODO: How to update settings.py for event/agent vocabularies::

    EVENT_OUTCOME_CHOICES = (
        ('', 'None'),
        ('http://purl.org/net/untl/vocabularies/eventOutcomes/#success', 'Success'),
        ('http://purl.org/net/untl/vocabularies/eventOutcomes/#failure', 'Failure'),
    )
    EVENT_TYPE_CHOICES = (
        ('', 'None'),
        ('http://id.loc.gov/vocabulary/preservation/eventType/fix', 'Fixity Check'),
        ('http://id.loc.gov/vocabulary/preservation/eventType/rep', 'Replication'),
        ('http://id.loc.gov/vocabulary/preservation/eventType/ing', 'Ingestion'),
        ('http://id.loc.gov/vocabulary/preservation/eventType/mig', 'Migration'),
    )
