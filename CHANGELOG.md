1.2.6
------

* Support Django 1.9 
* Drop support for < 1.9

1.2.5
-----

* Removed bare excepts for flake8 ([#89](
https://github.com/unt-libraries/django-premis-event-service/pull/89))

1.2.4
-----

* Raise max_length for linked object id in forms from 20 to 64 ([#84](
https://github.com/unt-libraries/django-premis-event-service/issues/84))
* Raise event search results (JSON + HTML) page sizes from 20 to 200 ([#85](
https://github.com/unt-libraries/django-premis-event-service/issues/85))
* Fix totalResults in JSON event search ([#86](
https://github.com/unt-libraries/django-premis-event-service/issues/86))
* Make return value for empty result sets (was empty list) same form as
populated result set but with empty entries list ([#87](
https://github.com/unt-libraries/django-premis-event-service/pull/87))
* Raise AtomPub event listing page size to 200 for consistency ([#88](
https://github.com/unt-libraries/django-premis-event-service/pull/88/))

1.2.3
-----

* Fix paging for event search results using linked object id as filter
* Gracefully fail on empty search result set using linked object id as filter

1.2.2
-----

* Removed deprecated calls to make compatible w/ Django 1.10

1.2.1
-----

* Fix broken PUT request handling (#72)

1.2.0
-----

* Added PREMIS v2.3 validation and tests
* PEP 8 conformity
* Assorted AtomPub fixes
* Update `codalib` requirement to 1.0.2
* Improve event search performance

1.1.0
-----

* Support Django 1.8 
* Drop support for < 1.7
* Use `codalib`
* Refactor Event search

1.0.0
-----

* Initial release.
