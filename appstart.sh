#!/bin/bash
/wait-for-mysqld.sh
python manage.py migrate
python manage.py runserver 0.0.0.0:80
