Installation
============

The project's README.rst file contains some basic installation instructions.
We'll elaborate a bit here:

Dependencies
------------

- Python 2.6+ (not Python 3)
- Django (Tested on 1.6.1, at least 1.3 or higher required)
- lxml (Ubuntu/Debian users should `apt-get build-dep python-lxml` first)

Before you begin
----------------

The instructions below assume that you have a Django project already created.
If you don't, you can create one using the "django-admin.py startproject" 
command (in an environment where Django has been installed).  The specifics
of where and how you create your project will depend on your specific hosting
preferences and needs.  Some understanding of WSGI hosting and Python virtual
environments is highly recommended before going forward.

Install
-------

To install this package, do one of the following:

- Place the premis_event_service folder in your Django project directory
  (alongside the manage.py file)
- Place the premis_event_service folder somewhere in your PYTHON_PATH
- Install using: pip install <path to django-premis-event-service>
  (activate your Django virtualenv before running) (NOT YET AVAILABLE)
- Install from PyPI using: pip install django-premis-event-service
  (activate your Django virtualenv before running) (NOT YET AVAILABLE)

Quick start
-----------

1. Update your INSTALLED_APPS setting as follows::

    INSTALLED_APPS = (
        ...
        'django.contrib.humanize',
        'premis_event_service',
    )

2. Define the following settings group (if you don't already have it) and
   ensure that it contains at least the entries shown below:

    TEMPLATE_CONTEXT_PROCESSORS = (
        'django.contrib.auth.context_processors.auth',
        'django.core.context_processors.debug',
        'django.core.context_processors.i18n',
        'django.core.context_processors.media',
        'django.core.context_processors.request',
    )

3. Add the MAINTENANCE_MSG setting to the bottom of your project settings::

    MAINTENANCE_MSG = ''  # Message to show during maintenance

4. Include the event service URLconf in your project urls.py like this (do not
   modify this line -- this app must be served from top-level URLs for now)::

    url(r'', include('premis_event_service.urls')),

5. Run `python manage.py syncdb` to create the event service models.

6. Start the development server and visit http://127.0.0.1:8000/premis/event/
   to see event information.

7. Visit http://127.0.0.1:8000/premis/agent/ to see agent information.
