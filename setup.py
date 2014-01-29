#! /usr/bin/env python
from setuptools import setup, find_packages

setup(
    name = "django-premis-event-service",
    version = "1.0",
    packages = find_packages(),

    # metadata (used during PyPI upload)
    author = "University of North Texas Libraries",
    description = "A Django application for storing and querying PREMIS Events",
    license = "BSD",
    keywords = "django PREMIS preservation",
    classifiers = [
        "Programming Language :: Python :: 2",
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
    long_description = """\
PREMIS Event Service
--------------------

The PREMIS Event Service is a Django application for storing and querying
events, represented internally according to the PREMIS Event specification.
"""
)
