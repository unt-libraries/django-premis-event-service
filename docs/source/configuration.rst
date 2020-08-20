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
=======================

1. Update your INSTALLED_APPS setting as follows::

    INSTALLED_APPS = (
        ...
        'django.contrib.humanize',
        'premis_event_service',
    )

2. Make sure you have a ``TEMPLATE_CONTEXT_PROCESSORS`` setting defined
   containing at least the entries shown below::

    TEMPLATE_CONTEXT_PROCESSORS = (
        'django.contrib.auth.context_processors.auth',
        'django.core.context_processors.debug',
        'django.core.context_processors.i18n',
        'django.core.context_processors.media',
        'django.core.context_processors.request',
    )

3. In your ``MIDDLEWARE`` setting, remove or comment out the
   ``CsrfViewMiddleware`` entry::

    MIDDLEWARE = (
        ...
        #'django.middleware.csrf.CsrfViewMiddleware',
        ...
    )

4. Add a ``MAINTENANCE_MSG`` setting at the bottom of the file::

    MAINTENANCE_MSG = ''  # Message to show during maintenance

Customizing the Controlled Vocabulary
=====================================

Deciding on Controlled Vocabulary Design
----------------------------------------

The Premis Event Service was designed to us a wide variety of or identifiers 
for values within PREMIS Event Objects. That being said there are some best 
practices that can be suggested to new a implementer.

It is advantageous for someone implementing the Premis Event Service to make 
use of existing controlled vocabularies whenever possible for some of the 
concepts that are used throughout the application.  For example the Library of 
Congress has added a number of `Preservation Vocabulary`_ entries to its 
`Authorities and Vocabularies Service`_. Starting with these identifiers for 
concepts such as "Fixity Check", "Replication", "Ingestion", or "Migration" is 
a suggestion unless there is a reason to deviate from these in a local 
implementation. 

.. _Preservation Vocabulary: http://id.loc.gov/vocabulary/preservation.html
.. _Authorities and Vocabularies Service: http://id.loc.gov/

Additional concepts that are not covered by the Library of Congress Authorities 
and Vocabularies Service are those for the outcome of an event,  for example 
“Success” and “Failure”.  The Premis Event Service has placeholders set aside 
for these values that utilize the controlled vocabularies at the University of
North Texas: http://purl.org/NET/untl/vocabularies/

The Premis Event Service will work without fully fleshed out controlled 
vocabularies, and the authors have worked to give examples with reasonable 
values which can be added to or modified to meet local needs.

Configuring a Custom Controlled Vocabulary
------------------------------------------

The Event Service makes no attempt to validate values given to it against any 
set of allowed values; it is up to your policies and integrations to enforce 
consistency across the events you store.

However, you can change the choices that are shown in the "Search" interface 
by adding some statements like these to your  ``settings.py`` file::

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
