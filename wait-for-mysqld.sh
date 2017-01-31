#!/bin/bash
while ! nc -z db 3306; do echo "waiting for mysqld..."; sleep 3; done
