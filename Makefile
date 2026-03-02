SHELL := /bin/bash

.PHONY: upgrade run seed fresh

upgrade:
	@export FLASK_APP=wsgi.py && flask db upgrade

run:
	@flask --app wsgi.py run --debug

seed:
	@export DATABASE_URL=postgresql+psycopg2://app_user:secret123@localhost:5432/webinar && python seed.py

fresh:
	@export DATABASE_URL=postgresql+psycopg2://app_user:secret123@localhost:5432/webinar && python reset_db.py
	@export DATABASE_URL=postgresql+psycopg2://app_user:secret123@localhost:5432/webinar && export FLASK_APP=wsgi.py && flask db upgrade
	@export DATABASE_URL=postgresql+psycopg2://app_user:secret123@localhost:5432/webinar && python seed.py
