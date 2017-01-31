#!/bin/bash
/wait-for-mysqld.sh
echo "Migrate..."
python manage.py migrate --settings=premis_event_service.config.settings.local
echo "Start app..."
python manage.py runserver 0.0.0.0:80 --settings=premis_event_service.config.settings.local

