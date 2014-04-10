=======================
Using the Event Service
=======================

There are two ways of using the PREMIS Event Service:

* using the web interface to view and manage events by hand
* using the APIs to create or query events from other software workflows

This document will cover how to use the web interface and admin site.
For information about the APIs, refer to the next section (:doc:`api`).

.. contents::
    :local:
    :depth: 2

Events
======

Browse All
----------

URL: ``http://[host]/event/``

Human readable HTML listing of events.

View One
--------

URL: ``http://[host]/event/[id]/``

Human readable HTML listing of a single event. Contains links to other 
formats/representations of the event, such as PREMIS XML.

Search
------

URL: ``http://[host]/event/search/``

Web interface for searching events. Events can be filtered by outcome, type, 
start/end dates, or Linked Object ID.

Browsing Agents
===============

Browse All
----------

URL: ``http://[host]/agent/``

Human readable HTML listing of agents.

View One
--------

URL: ``http://[host]/agent/[id]/``

Human readable HTML listing of a single agent. Contains links to other 
formats/representations of the agent, such as PREMIS XML.
