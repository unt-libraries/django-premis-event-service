# PREMIS Event Service

![image](https://github.com/unt-libraries/django-premis-event-service/actions/workflows/test.yml/badge.svg?branch=master)

PREMIS Event Service is a Django application for managing PREMIS Events in a
structured, centralized, and searchable manner.

## Purpose

The purpose of this application is to provide a straightforward way to send
PREMIS-formatted events to a central location to be stored and retrieved. In
this fashion, it can serve as an event logger for any number of services that
happen to wish to use it. PREMIS is chosen as the underlying format for events
due to its widespread use in the digital libraries world.

## Dependencies

* Python 3.9
* Django 4.2
* lxml (requires system libraries such as libxml2 and libxslt)

## Documentation

Documentation, including installation instructions, can be viewed online at:

https://premis-event-service.readthedocs.io/

The documentation is also browsable locally from within the ``docs``
directory of this repository. You can read the source files in plain text
from the ``docs/source`` directory, or generate your own local copy of the
HTML files by doing the following:

1. Make sure Sphinx is installed (``pip install sphinx``)
2. ``cd docs``
3. ``make html``
4. Open ``index.html`` (generated in ``docs/build/html``)


## License

See LICENSE.


## Acknowledgements

The PREMIS Event Service was developed at the UNT Libraries and has been worked on
by a number of developers over the years including

* Kurt Nordstrom
* [Joey Liechty](http://github.com/yeahdef)
* [Lauren Ko](http://github.com/ldko)
* Stephen Eisenhauer
* [Mark Phillips](http://github.com/vphill)
* [Damon Kelley](http://github.com/damonkelley)
* Reed Underwood
* Andromeda Yelton (MIT)
* [Gio Gottardi](http://github.com/somexpert)
* [Madhulika Bayyavarapu](http://github.com/madhulika95b)
* [Gracie Flores-Hays](https://github.com/gracieflores)
* [Trey Clark](https://github.com/clarktr1)

If you have questions about the project feel free to contact Mark Phillips at mark.phillips@unt.edu

## Developing
There are two ways to develop the Event service Django app. One is natively using an SQLite backend. The other is using a MySQL backend for storage inside a Docker container.

### Developing Natively Using SQLite

[SQLite](https://sqlite.org/)

### Clone the repository

```
$ git clone https://github.com/unt-libraries/django-premis-event-service.git 
$ cd django-premis-event-service
```

### Create & Activate a Virtual Environment
```sh
$ python -m venv env
$ source env/bin/activate
```

### Install Requirements
```
$ pip install '.[test]'
```

### Run the tests
This will run both unit tests with `pytest` and linting with [`ruff`](https://docs.astral.sh/ruff/).
```sh
$ tox
```

### Apply the most recent migrations
```sh
$ python manage.py migrate
```


### Start the development server
```sh
$ python manage.py runserver
```
Navigate to ``http://localhost:8000/event/`` to view the app. 


## Developing Using Docker and MySQL as a Backend

### Install Docker
Install [Docker](https://docs.docker.com/engine/install/). Instructions differ based on operating system.


### Clone the repository
```sh
$ git clone https://github.com/unt-libraries/django-premis-event-service.git 
$ cd django-premis-event-service
```


### Starting the app

```sh
# start the app (this will spin two containers: db and web)
$ docker compose up -d

# apply the most recent migration
$ docker compose run --rm web python manage.py migrate

# optional: add a superuser in order to login to the admin interface
$ docker compose run --rm web python manage.py createsuperuser
```

Navigate to ``http://localhost:8000/event/`` to view the app.


The code is in a volume that is shared between your workstation and the app container, which means any edits you make on your workstation will also be reflected in the Docker container. No need to rebuild the container to pick up changes in the code.

However, if the `pyproject.toml` changes, it is important that you rebuild the app container for those packages to be installed. This is something that could happen when switching between feature branches; when installing new dependencies during development; or when pulling updates from the remote.

```sh

  # stop the app
  $ docker compose stop

  # remove the app container
  $ docker compose rm web

  # rebuild the app container
  $ docker compose build web # under some circumstances, you may need to use the --no-cache switch, e.g. upstream changes to packages the app requires

  # start the app
  $ docker compose up -d db web
```
### Viewing the logs
```sh
$ docker compose logs -f
```


### Running the Tests

To run the tests via Tox, use this command. If you are using podman-compose, swap the word docker 
with podman (see ``Developing with Podman and Podman-Compose`` below).

```sh
$ docker compose run --rm web tox
```

## Developing with Podman and Podman-Compose


### Install or Enable Podman

[Podman Installation](https://podman.io/getting-started/installation)

### Install Podman-Compose

[Podman-Compose Installation](https://github.com/containers/podman-compose)

You will follow the same steps as above, starting with ``Clone the repository``. For all of the 
docker steps, you will have to replace the word ``docker`` with ``podman``.

If you have SELinux, you may need to temporarily add ``:Z`` to the base volumes in the 
``docker-compose.yml``. It will look like ``.:/app/:Z``. You may also need to use ``sudo`` for 
your podman-compose commands.
