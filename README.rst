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
* Django (tested on 1.6.1; at least 1.3 or higher required)
* lxml (requires libxml2-dev to be installed on your system)


Documentation
-------------

Documentation, including installation instructions, can be viewed online at:

http://premis-event-service.readthedocs.org/

The documentation is also browsable locally from within the ``docs`` 
directory of this repository. You can read the source files in plain text 
from the ``docs/source`` directory, or generate your own local copy of the 
HTML files by doing the following:

1. Make sure Sphinx is installed (``pip install sphinx``)
2. ``cd docs``
3. ``make html``
4. Open ``index.html`` (generated in ``docs/build/html``)


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
* Damon Kelley

If you have questions about the project feel free to contact Mark Phillips at mark.phillips@unt.edu

Developing
----------

To take advantage of the dev environment that is already configured, you need to have Docker and Docker Compose installed.

Install Docker_

.. _Docker: https://docs.docker.com

Install Docker Compose

.. code-block :: sh

  $ pip install docker-compose


Clone the repository.

.. code-block :: sh

  $ git clone https://github.com/unt-libraries/django-premis-event-service.git
  $ cd django-premis-event-service


Start the app and run the migrations.

.. code-block :: sh

  # start the app
  $ docker-compose up -d

  # optional: add a superuser in order to login to the admin interface
  $ docker-compose run --rm web ./manage.py createsuperuser


The code is in a volume that is shared between your workstation and the web container, which means any edits you make on your workstation will also be reflected in the Docker container. No need to rebuild the container to pick up changes in the code.

However, if the requirements files change, it is important that you rebuild the web container for those packages to be installed. This is something that could happen when switching between feature branches, or when pulling updates from the remote.

.. code-block :: sh

  # stop the app
  $ docker-compose stop

  # remove the web container
  $ docker-compose rm web

  # rebuild the web container
  $ docker-compose build web

  # start the app
  $ docker-compose up -d


Running the Tests
-----------------
To run the tests via Tox, use this command.

.. code-block :: sh

  $ docker-compose run --rm web tox


To run the tests only with the development environment.

.. code-block :: sh

  $ docker-compose run --rm web py.test

