#!/bin/bash
/wait-for-mysqld.sh
echo "Migrate..."
pipenv run python manage.py migrate --settings=tests.settings
echo "Start app..."
pipenv run python manage.py runserver 0.0.0.0:80 --settings=tests.settings
