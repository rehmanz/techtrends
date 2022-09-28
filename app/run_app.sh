#!/bin/sh

pipenv run python init_db.py
exec pipenv run python app.py
