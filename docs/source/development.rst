===========
Development
===========

Here, you will find some information helpful if you plan on developing upon or
making changes to the Event Service source code itself.

Project Structure
=================

The PREMIS Event Service is structured as a common Python project, providing a
Python package named `premis_event_service` which is a Django app::

    premis_event_service/ # The Django app itself. Technically a Python package.
        admin.py          ## Customizes the Django admin interface
        coda/             ## Some supporting modules we need for some tasks
            anvl.py
            bagatom.py
            __init__.py   ### Marks this directory as a valid Python package
            util.py
        forms.py          ## Form processing code
        helpy.py
        __init__.py       ## Marks this directory as a valid Python package
        models.py         ## Database model definitions
        populator.py
        presentation.py
        settings.py       ## Wrapper for project settings file with custom defaults
        templates/        ## HTML templates
        urls.py           ## URL routing patterns
        views.py          ## View generation code

If you're not sure where to look for something, `urls.py` is usually the best
place to start.  There you'll find a list of every URL pattern handled by the
application, along with its corresponding view (found in `views.py`) and 
arguments.

Models
======

Models define the data objects Django keeps in its database. The PREMIS Event 
Service defines these three:

* Event - Represents an event.
* Agent - Represents an agent you've defined using the Django admin interface.
* LinkObject - Contains an identifier for an object in your preservation 
  workflow. Exists for the purpose of relating multiple events that pertain to 
  the same object.

See ``premis_event_service/models.py`` for the full definitions to these models.

Views
=====

View are functions (or sometimes classes) that Django calls upon to generate 
the result of a request. Usually this just means rendering some HTML from a 
template and serving it, but sometimes this involves form processing and API 
interactions as well. Django decides which view to run based on what's defined 
in ``urls.py``.

See ``premis_event_service/views.py`` for the full source code to all the views 
provided by the Event Service.
