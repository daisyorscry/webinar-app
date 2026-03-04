SHELL := /bin/bash

.PHONY: upgrade run seed fresh wait-db

wait-db:
	@python wait_for_db.py

upgrade:
	@$(MAKE) wait-db
	@export FLASK_APP=wsgi.py && flask db upgrade

run:
	@flask --app wsgi.py run --debug

seed:
	@$(MAKE) wait-db
	@python seed.py

fresh:
	@$(MAKE) wait-db
	@python reset_db.py
	@export FLASK_APP=wsgi.py && flask db upgrade
	@python seed.py
