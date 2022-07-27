#!/bin/bash
python manage.py makemigrations
python manage.py migrate
python manage.py makemigrations beak
python manage.py migrate beak