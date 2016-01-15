#! /usr/bin/env python
import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

install_requires = [
    'lxml >= 3.0.0',
    'codalib>=1.0.0'
]

setup(
    name="django-premis-event-service",
    version="1.0.0",
    packages=['premis_event_service'],
    include_package_data=True,
    license="BSD",
    description="A Django application for storing and querying PREMIS Events",
    long_description=README,
    keywords="django PREMIS preservation",
    author="University of North Texas Libraries",
    url="https://github.com/unt-libraries/django-premis-event-service",
    install_requires=install_requires,
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
)
