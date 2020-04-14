#! /usr/bin/env python
import os
from setuptools import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

install_requires = [
    'lxml >= 3.0.0',
    'codalib'
]

dependency_links = ['codalib @ git+https://github.com/unt-libraries/codalib@master']

setup(
    name="django-premis-event-service",
    version="1.2.5",
    packages=find_packages(exclude=["tests", ]),
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
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
)
