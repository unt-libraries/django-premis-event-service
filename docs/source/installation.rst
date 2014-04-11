============
Installation
============

The project's README.rst file contains some basic installation instructions.
We'll elaborate a bit in this section.

.. contents::
    :local:
    :depth: 2

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

To install this package, do **one (1)** of the following:

- Place the ``premis_event_service`` folder in your Django project directory
  (alongside the ``manage.py`` file)
- Place the ``premis_event_service`` folder somewhere in your PYTHON_PATH
.. - Install using: pip install <path to django-premis-event-service>
..   (activate your Django virtualenv before running) (NOT YET AVAILABLE)
.. - Install from PyPI using: pip install django-premis-event-service
..   (activate your Django virtualenv before running) (NOT YET AVAILABLE)

Quick start
-----------

1. Follow the Mandatory Configuration instructions in :doc:`configuration`.

2. Include the event service URLconf in your project ``urls.py`` like this (do 
   not modify this line -- this app must be served from top-level URLs for 
   in its current state)::

    url(r'', include('premis_event_service.urls')),

3. Run ``python manage.py syncdb`` to create the event service models. If 
   asked to create a superuser account, follow the prompts to do so. You will 
   need at least one superuser account.

4. Start the development server using: ``python manage.py runserver``

5. Visit http://127.0.0.1:8000/admin/ in a web browser and log in using your 
   superuser credentials.

6. Continue to :doc:`administration` to begin setting up Agents.
