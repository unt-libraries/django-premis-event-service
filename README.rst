PREMIS Event Service
====================

.. image:: https://github.com/unt-libraries/django-premis-event-service/actions/workflows/test.yml/badge.svg?branch=master
    :target: https://github.com/unt-libraries/django-premis-event-service/actions

PREMIS Event Service is a Django application for managing PREMIS Events in a
structured, centralized, and searchable manner.

Purpose
-------

The purpose of this application is to provide a straightforward way to send
PREMIS-formatted events to a central location to be stored and retrieved. In
this fashion, it can serve as an event logger for any number of services that
happen to wish to use it. PREMIS is chosen as the underlying format for events
due to its widespread use in the digital libraries world.

Dependencies
------------

* Python 3
* Django 2.2
* lxml (requires libxml2-dev to be installed on your system)
* pipenv


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
* Reed Underwood
* Andromeda Yelton (MIT)
* Madhulika Bayyavarapu
* Gracie Flores-Hays

If you have questions about the project feel free to contact Mark Phillips at mark.phillips@unt.edu

Developing
----------
There are two (supported) ways to develop the PREMIS event service Django app. One is natively using an SQLite backend. The other is using a MySQL backend for storage inside a Docker container.

Developing Natively Using SQLite_
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _SQLite: https://sqlite.org/

Clone the repository
""""""""""""""""""""

.. code-block :: sh

  $ git clone https://github.com/unt-libraries/django-premis-event-service.git # check the repo for the latest official release if you don't want the development version at HEAD on the master branch
  $ cd django-premis-event-service


Install the requirements using pipenv_
""""""""""""""""""""""""""""""""""""""

.. _pipenv: https://pipenv.readthedocs.io/en/latest/

.. code-block :: sh

    $ pipenv --python 3.7 # (to create the virtualenv)
    $ pipenv install --dev
    $ pipenv shell # (to enter the virtualenv)
    $ exit # (to leave the virtualenv)

If you need to generate a requirements.txt file, you can do so with
``pipenv lock -r > requirements.txt``.


Run the tests using tox_
""""""""""""""""""""""""

.. _tox: https://tox.readthedocs.io/en/latest/

.. code-block :: sh

    $ tox

Apply the migrations
""""""""""""""""""""

.. code-block :: sh

    $ python manage.py migrate


Start the development server
""""""""""""""""""""""""""""

.. code-block :: sh

    $ python manage.py runserver 9999


This will start the development server listening locally on port 9999. You may want to change the port number, passed as the first argument to the ``runserver`` command.


View the web UI in a browser
""""""""""""""""""""""""""""

Navigate to ``http://localhost:9999/event/`` (or whatever port you chose) to see the UI of the app.


Developing Using Docker and MySQL as a Backend
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Install Docker_
"""""""""""""""

.. _Docker: https://docs.docker.com

On Debian-derived Linux distros, you can use ``apt-get`` to install. If you're on a different OS, check the Docker site for instructions.


Install Docker Compose
""""""""""""""""""""""

.. code-block :: sh

  $ pip install docker-compose

Alternatively, you may want to install ``docker-compose`` using your system's package manager.


Clone the repository
""""""""""""""""""""

.. code-block :: sh

  $ git clone https://github.com/unt-libraries/django-premis-event-service.git # check the repo for the latest official release if you don't want the development version at HEAD on the master branch
  $ cd django-premis-event-service


Starting the app
""""""""""""""""

.. code-block :: sh

  # start the app
  $ docker-compose up -d db app

  # If you make changes to the models, create and apply a migration
  $ docker-compose run manage makemigrations
  $ docker-compose run manage migrate

  # optional: add a superuser in order to login to the admin interface
  $ docker-compose run manage createsuperuser


View the web UI in a browser
""""""""""""""""""""""""""""

Navigate to ``http://localhost:8000/event/`` to see the UI of the app. The port can be changed by editing the ``docker-compose.yml`` file.


The code is in a volume that is shared between your workstation and the app container, which means any edits you make on your workstation will also be reflected in the Docker container. No need to rebuild the container to pick up changes in the code.

However, if the Pipfile.lock changes, it is important that you rebuild the app container for those packages to be installed. This is something that could happen when switching between feature branches; when installing new dependencies during development; or when pulling updates from the remote.

.. code-block :: sh

  # stop the app
  $ docker-compose stop

  # remove the app container
  $ docker-compose rm app

  # rebuild the app container
  $ docker-compose build app # under some circumstances, you may need to use the --no-cache switch, e.g. upstream changes to packages the app requires

  # start the app
  $ docker-compose up -d db app


Viewing the logs
""""""""""""""""

.. code-block :: sh

    $ docker-compose logs -f


Running the Tests
"""""""""""""""""

To run the tests via Tox, use this command. If you are using podman-compose, swap the word docker 
with podman (see ``Developing with Podman and Podman-Compose`` below).

.. code-block :: sh

  $ docker-compose run --rm test


Developing with Podman and Podman-Compose
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Install or Enable Podman_
"""""""""""""""""""""""""

.. _Podman: https://podman.io/getting-started/installation

Install Podman-Compose_
"""""""""""""""""""""""

.. _Podman-Compose: https://github.com/containers/podman-compose

.. code-block :: sh

  $ sudo dnf install podman-compose

You will follow the same steps as above, starting with ``Clone the repository``. For all of the 
docker steps, you will have to replace the word ``docker`` with ``podman``.

If you have SELinux, you may need to temporarily add ``:Z`` to the base volumes in the 
``docker-compose.yml``. It will look like ``.:/app/:Z``. You may also need to use ``sudo`` for 
your podman-compose commands.
