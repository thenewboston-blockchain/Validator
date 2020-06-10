#!/bin/bash

python3 scripts/dump_database.py
python3 manage.py makemigrations
python3 manage.py migrate
