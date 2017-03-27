==================
Technical Overview
==================

.. contents::
    :local:
    :depth: 2

Events
======

A standard PREMIS event encoded as XML looks something like the following::

    <premis:event xmlns:premis="info:lc/xmlns/premis-v2">
        <premis:eventType>
            http://purl.org/net/meta/vocabularies/preservationEvents/#MigrateSuccess
        </premis:eventType>
        <premis:linkingAgentIdentifier>
            <premis:linkingAgentIdentifierValue>
                http://metaarchive.org/agent/metaMigrateSuccess
            </premis:linkingAgentIdentifierValue>
            <premis:linkingAgentIdentifierType>
                http://purl.org/net/meta/vocabularies/identifier-qualifiers/#URL
            </premis:linkingAgentIdentifierType>
        </premis:linkingAgentIdentifier>
        <premis:eventIdentifier>
            <premis:eventIdentifierType>
                http://purl.org/net/meta/vocabularies/identifier-qualifiers/#UUID
            </premis:eventIdentifierType>
            <premis:eventIdentifierValue>
                e8ee3b1a8c9e4a5daf0a1e0446383d90
            </premis:eventIdentifierValue>
        </premis:eventIdentifier>
        <premis:eventDetail>
            Verification of data at /data3/meta-r1-003_dropbox/meta106w
        </premis:eventDetail>
        <premis:eventOutcomeInformation>
            <premis:eventOutcomeDetail>
                Checking content after cache server migration
            </premis:eventOutcomeDetail>
            <premis:eventOutcome>
                http://purl.org/net/meta/vocabularies/eventOutcomes/#success
            </premis:eventOutcome>
        </premis:eventOutcomeInformation>
        <premis:eventDateTime>
            2011-01-25 16:39:49
        </premis:eventDateTime>
        <premis:linkingObjectIdentifier>
            <premis:linkingObjectIdentifierType>
                http://purl.org/net/meta/vocabularies/identifier-qualifiers/#ARK
            </premis:linkingObjectIdentifierType>
            <premis:linkingObjectIdentifierValue>
                ark:/67531/meta106w
            </premis:linkingObjectIdentifierValue>
            <premis:linkingObjectRole/>
        </premis:linkingObjectIdentifier>
    </premis:event>

This is a lot at first glance, but the pieces are more or less logical. The 
relevant things that a given PREMIS event record keeps track of are the 
following:

- **Event Identifier** - This is a unique identifier assigned to every event when 
  it is entered into the system. This is what is used to reference given event.
- **Event Type** - This is an arbitrary value to categorize the kind of event 
  we're logging. Examples might include fixity checking, virus scanning or replication.
- **Event Time** - This is a timestamp for when the event itself occurred.
- **Event Added** - This is a timestamp for when the event was logged.
- **Event Outcome** - This is the simple description of the outcome. Usually 
  something like "pass" or "fail".
- **Outcome Details** - A more detailed record of the outcome. Perhaps output from 
  a secondary program might go here.
- **Agent** - This is the identifier for the agent that initiated the event. An 
  agent can be anything, from a person, to an institution, to a program. The 
  PREMIS event service will also allow you to track agent entries as well.
- **Linked Objects** - These are identifiers for relevant objects that the event 
  is associated with. If your system uses object identifiers, you could put 
  those identifiers here when an event pertains to them.

It is important to note that most of the values that you use in a given PREMIS 
event record are arbitrary. You decide on your own values and vocabularies, 
and use what makes sense to you. It doesn't enforce any sort of constraints as 
far as that goes. The service is responsible for indexing all PREMIS events 
sent to it and providing retrieval for them. Basic retrieval is on a 
per-identifier basis, but it is plausible to assume that you may wish to 
request events based on date added, agent used, event type, event outcome, or 
a combination of these factors.

Agents
======

The PREMIS metadata specification defines a separate spec for agents that 
looks like the following::

    <?xml version="1.0"?>
    <premis:agent xmlns:premis="info:lc/xmlns/premis-v2">
        <premis:agentIdentifier>
            <premis:agentIdentifierValue>
                MigrateSuccess
            </premis:agentIdentifierValue>
            <premis:agentIdentifierType>
                FDsys:agent
            </premis:agentIdentifierType>
        </premis:agentIdentifier>
        <premis:agentName>
            http://institution.edu/agent/metaMigrateSuccess
        </premis:agentName>
        <premis:agentType>softw</premis:agentType>
    </premis:agent>

As you can see from the above example, the agent's identifier above 
corresponds with the agent in the event example. You are able to create and 
register agents through the administrative panel on the PREMIS service; 
see the :doc:`administration` section to learn how.
