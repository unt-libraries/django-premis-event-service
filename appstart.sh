#!/bin/bash
/wait-for-mysqld.sh
echo "Migrate..."
python manage.py migrate --settings=tests.settings
echo "Start app..."
python manage.py runserver 0.0.0.0:80 --settings=tests.settings

