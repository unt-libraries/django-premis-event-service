==============
Administration
==============

This section outlines the initial work needed after installation in order to 
prepare your Event Service for use.

.. contents::
    :local:
    :depth: 2

Manage User Accounts
====================

To create an admin account, run ``python manage.py createsuperuser`` and follow the prompts.

To manage or create other user accounts, do the following:

1. Visit the Django admin interface (``http://[host]/admin/``) in a web browser.
2. Log in using your superuser account.
3. Click **Users**. This takes you to the list of Users.
4. Click the **Add user** button near the top-right corner of the page.
5. Fill and submit the form.

Keep in mind that any account needing the ability to also administer user 
accounts using the admin interface will need to be given "superuser" status.

Create an Agent
===============

Every event stored in the Event Service must be associated with an Agent. 
Agents merely represent entities that produce events. In many cases these are 
software processes (e.g. a web application or a script), but an agent can also 
be a person, an institution, or anything else.

To create a new agent (or to manage existing ones), do the following:

1. Visit the Django admin interface (``http://[host]/admin/``) in a web browser.
2. Log in using your superuser account (if you haven't already).
3. Click **Agents**. This takes you to the list of Agents, which will be empty 
   at first.
4. Click the **Add agent** button near the top-right corner of the page.
5. Fill and submit the form.

Create as many agents as you have a need for.
