#!/bin/bash
# Delete beak/migrations folder, delete db.sqlite3
python manage.py makemigrations
python manage.py migrate
python manage.py makemigrations beak
python manage.py migrate beak