============
Installation
============

The project's README.rst file contains some basic installation instructions.
We'll elaborate a bit in this section.

.. contents::
    :local:
    :depth: 2

Dependencies
============

- Python 3.7.x
- Django 2.2
- libxml2-dev libxslt-dev
- Django Admin - ``django.contrib.admin``

Important security warning
==========================

This application **does not** attempt to authenticate requests or differentiate 
between clients in any way -- even for write and edit operations via the API. 
Do not simply expose the application to the public in your server configuration.
Instead, use a network firewall to whitelist the server to authorized clients, 
or use a web server configuration directive (such as Apache's 
``<LimitExcept GET>``) to set up who is allowed to POST/PUT/DELETE events.

Install
=======

1. Install the package. ::

    $ pip install git+https://github.com/unt-libraries/django-premis-event-service
    $ # check https://github.com/unt-libraries/django-premis-event-service/releases for the latest release

2. Add ``premis_event_service`` to your ``INSTALLED_APPS``. Be sure to add ``django.contrib.admin`` if it is not already present. ::

    INSTALLED_APPS = (
        'django.contrib.admin',
        # ...
        'premis_event_service',
    )

4. Include the URLs. ::

    urlpatterns = [
        url(r'', include('premis_event_service.urls'))
        # ...
        url(r'^admin/', include(admin.site.urls)),
    ]


5. Migrate the database. ::

   $ python manage.py migrate

6. Continue to :doc:`administration` to begin setting up Agents.
