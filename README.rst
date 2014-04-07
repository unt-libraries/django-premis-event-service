====================
PREMIS Event Service
====================

PREMIS Event Service is a Django application for managing PREMIS Events in a
structured, centralized, and searchable manner.

Purpose
-------

The purpose of this microservice is to provide a straightforward way to send 
PREMIS-formatted events to a central location to be stored and retrieved. In 
this fashion, it can serve as an event logger for any number of services that 
happen to wish to use it. PREMIS is chosen as the underlying format for events 
due to its widespread use in the digital libraries world.

Dependencies
------------

* Python 2.6+ (not Python 3)
* Django (Tested on 1.6.1, at least 1.3 or higher required)
* lxml

Install
-------

Installation instructions can be found in docs/source/installation.rst


Documentation
-------------

Documentation can be browsed online on Read The Docs:

http://premis-event-service.readthedocs.org/

The documentation is located in the ``docs`` directory. There, you will find a
``source`` directory containing the actual documentation text, as well as a
Sphinx (http://sphinx-doc.org) Makefile. If you have Sphinx installed
(``pip install sphinx``) and run ``make html``, a more readable HTML version 
will be generated in the ``docs/build/html`` directory.


License
-------

See LICENSE.


Acknowledgements
----------------

The Premis Event Service was developed at the UNT Libraries and has been worked on 
by a number of developers over the years including

* Kurt Nordstrom   
* Joey Liechty   
* Lauren Ko   
* Stephen Eisenhauer   
* Mark Phillips   

If you have questions about the project feel free to contact Mark Phillips at mark.phillips@unt.edu
