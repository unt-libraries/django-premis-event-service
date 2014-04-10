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


Examples
========

TODO
