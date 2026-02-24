#!/bin/bash
while ! nc -z db 3306;
do
  echo "waiting for mysqld...";
  sleep 3;
done
echo "Migrate..."
python manage.py migrate
echo "Start app..."
python manage.py runserver 0.0.0.0:8000