===
API
===

The bulk of event creation using the Event Service will probably take place 
via software as opposed to by hand. This section explains the AtomPub API 
(Application Programming Interface) used for interacting with the Event 
Service from your custom applications and scripts.

.. contents::
    :local:
    :depth: 2

Introduction
============

The PREMIS Event Service uses REST to handle the message passing between 
client and server. To better provide a standard set of conventions for this, 
we have elected to follow the AtomPub protocol for POSTing and GETing events 
from the system. The base unit for AtomPub is the Atom "entry" tag, which is 
what gets sent back and forth. The actual PREMIS metadata is embedded in the 
entry's "content" tag. There is a lot more to AtomPub than that, but for the 
purpose of this document, it is helpful to just view the Atom entry as an 
"envelope" for the PREMIS XML.

API URL Structure
=================

APIs for communicating with the Event Service programmatically are located
under the ``/APP/`` URL tree:

/APP/
-----

AtomPub service document

The service document is an XML file that explains, to an AtomPub aware client, 
what services and URLs exist at this site. It's an integral part of the 
AtomPub specification, and allows for things like auto-discovery.

/APP/event/
-----------

AtomPub feed for event entries

Accepts parameters:

* start - This is the index of the first record that you want...it starts indexing at 1.
* count - This is the number of records that you want returned.
* start_date - This is a date (or partial date ) in ISO8601 format that indicates the earliest
record that you want.
* end_date - This is a date that indicates the latest record that you want.
* type - This is a string identifying a type identifier (or partial identifier) that you want to
filter events by
* outcome - This is a string identifying an outcome identifier (partial matching is supported)
* link_object_id - This is an identifier that specifies that we want events pertaining to a
particular object
* orderdir - This defaults to 'ascending'. Specifying 'descending' will return the records in
reverse order.
* orderby - This parameter specifies what field to order the records by. The valid fields are
currently: event_date_time (default), event_identifier, event_type, event_outcome

For the human-viewable feeds, the parameters are the same, except, instead of using a
'start' parameter, it uses a 'page' parameter, because of the way it paginates the output (see
below).

Also serves as a POST point for new entries.

Issuing a 'GET' to this URL will return an Atom feed of entries that represent 
PREMIS events.

This is the basic form of aggregation that AtomPub uses. Built into the Atom 
feed are tags thatallow for easy pagination, so crawlers will be able to 
process received data in manageable chunks. Additionally, this URL will accept 
a number of GET arguments, in order to filter the results that are returned.

This is also the endpoint for adding new events to the system, in which case a 
PREMIS Event is sent within an Atom entry in the form of an HTTP POST request.

/APP/event/<id>/
----------------

Permalink for Atom entry for a given event

This is the authoritative link for a given PREMIS Event entry, based upon the 
unique identifier that each event is assigned when it is logged into the 
system. It returns the event record contained within an Atom entry.

/APP/agent/
-----------

AtomPub feed for agent entries

Issuing a 'GET' request here returns an AtomPub feed of PREMIS Agent records. 
Because there will be far less agents than events in a given system, it is 
not known that we'll build search logic into this URL.

According to the AtomPub spec, this would be where we'd allow adding new 
Agents via POST, but because there are likely so few times that we'd need to 
add Agents, we would just as well leave this to be done through the admin 
interface.

/APP/agent/<id>/
----------------

Permalink for Atom entry for a given agent

The authoritative link for a given PREMIS Agent entry, based on the agent's 
unique id. Next are the URLs designed for human consumption.

Example
=======

.. highlight:: xml
   :linenothreshold: 5

Imagine that we have just completed a mass server-to-server data copy, and 
as part of that migrated data we have a directory called ``object_123/`` which 
contains a collection of files that represents a migrated digital object. 
This digital object conveniently enough, has the localidentifier (for our 
system) of ``object_123``.

We have a script ``validate_object`` that we can run 
on our objects to make certain that the files match a previously stored 
fixity digest and are intact after this migration. In this case, we wish to 
log an event of the validation in order to properly track our actions. To begin 
with, we run the ``validate_object`` script on our directory and wait for it to 
run.

Let's say that it runs and comes back with an 
error: ``Validation of object_123/ failed Details: Generated sum for 
object_123/data/pic_002.tif does not match stored value``. Obviously, we have 
to deal with the problem at some point, but right now we just want to log an 
event that will accurately reflect the results of the script. So, we create 
a PREMIS event XML tree::

    <premis:event xmlns:premis="info:lc/xmlns/premis-v2">
        <premis:eventType>
            validateObject
        </premis:eventType>
        <premis:linkingAgentIdentifier>
            <premis:linkingAgentIdentifierValue>
                validateObjectScript
            </premis:linkingAgentIdentifierValue>
            <premis:linkingAgentIdentifierType>
                Program
            </premis:linkingAgentIdentifierType>
        </premis:linkingAgentIdentifier>
        <premis:eventIdentifier>
            <premis:eventIdentifierType>
                TEMP
            </premis:eventIdentifierType>
            <premis:eventIdentifierValue>
                TEMP
            </premis:eventIdentifierValue>
        </premis:eventIdentifier>
        <premis:eventDetail>Validation of object
            object_123
        </premis:eventDetail>
        <premis:eventOutcomeInformation>
            <premis:eventOutcomeDetail>
                Generated sum for object_123/data/pic_002.tif does not match stored value
            </premis:eventOutcomeDetail>
            <premis:eventOutcome>
                Failure
            </premis:eventOutcome>
        </premis:eventOutcomeInformation>
        <premis:eventDateTime>
            2011-01-27 16:39:49
        </premis:eventDateTime>
        <premis:linkingObjectIdentifier>
            <premis:linkingObjectIdentifierType>
                Local Identifier
            </premis:linkingObjectIdentifierType>
            <premis:linkingObjectIdentifierValue>
                object_123
            </premis:linkingObjectIdentifierValue>
            <premis:linkingObjectRole />
        </premis:linkingObjectIdentifier>
    </premis:event>

As you can see, the values chosen for the tags in the PREMIS event XML are 
arbitrary, and it is the responsibility of the user to select something that 
makes sense in the context of their organization. One thing to note is that 
the values for the ``eventIdentifierType`` and ``eventIdentifierValue`` will be 
overwritten, because the Event Service manages the event identifiers, and 
assigns new ones upon ingest.

Now, in order to send the event to the Event Service, it must be wrapped in an 
Atom entry, so the following Atom wrapper XML tree is created::

    <entry xmlns="http://www.w3.org/2005/Atom">
        <title>PREMIS event entry for object_123</title>
        <id>PREMIS event entry for object_123</id>
        <updated>2011-­‐01-­‐27T16:40:30Z</updated>
        <author>
            <name>Object Verification Script</name>
        </author>
        <content type="application/xml">
            <premis:event xmlns:premis="http://www.loc.gov/standards/premis/v1">
                ...
            </premis:event>
        </content>
    </entry>

(With the previously-generated PREMIS XML going inside of the "content" tag.)

Now that the entry is generated and wrapped in a valid Atom document, it is 
ready for upload. In order to do this, we POST the Atom XML to the 
``/APP/event/`` URL.

When the Event Service receives the POST, it reads the content and parses 
the XML. If it finds a valid XML PREMIS event document, it will assign the 
event an identifier, index the values and save them, and then generate a 
return document, also wrapped in an Atom entry. It will look something like::

    <entry xmlns="http://www.w3.org/2005/Atom">
        <title>bfa2cf2c2a4f11e089b3005056935974</title>
        <id>bfa2cf2c2a4f11e089b3-005056935974</id>
        <updated>2011-01-27T16:40:30Z</updated>
        <author>
            <name>Object Verification Script</name>
        </author>
        <content type="application/xml">
            <premis:event xmlns:premis="http://www.loc.gov/standards/premis/v1">
                <premis:eventType>validateObject</premis:eventType>
                <premis:linkingAgentIdentifier>
                    <premis:linkingAgentIdentifierValue>
                        validateObjectScript
                    </premis:linkingAgentIdentifierValue>
                    <premis:linkingAgentIdentifierType>
                        Program
                    </premis:linkingAgentIdentifierType>
                </premis:linkingAgentIdentifier>
                <premis:eventIdentifier>
                    <premis:eventIdentifierType>
                        UUID
                    </premis:eventIdentifierType>
                    <premis:eventIdentifierValue>
                        bfa2cf2c2a4f11e089b3-005056935974
                    </premis:eventIdentifierValue>
                </premis:eventIdentifier>
                ...
            </premis:event>
        </content>
    </entry>

As you can see, the identifier has been changed to a UUID, which, in this 
case, is ``bfa2cf2c2a4f11e089b3-­‐005056935974``. This identifier is unique 
and will be what the microservice will use to refer to that individual event 
in the future.

If the POST is successful, the updated record will be returned, along with a 
status of "200". If the status is something else, there was an error, and 
the event cannot be considered to have been reliably recorded.

Later, when we (or, perhaps, another script) wish to review the event to 
find out what went wrong with the file validation, we would access it by 
sending an HTTP GET request to 
``/APP/event/bfa2cf2c2a4f11e089b3-005056935974``, which would return an Atom 
entry containing the final event record, which we could then analyze and use 
for whatever purposes desired.
