SHELL := /bin/bash

.PHONY: upgrade run seed seed-certificate seed-all fresh wait-db

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

seed-certificate:
	@$(MAKE) wait-db
	@python seed_certificate_demo.py

seed-all:
	@$(MAKE) wait-db
	@python seed.py
	@python seed_certificate_demo.py

fresh:
	@$(MAKE) wait-db
	@python reset_db.py
	@export FLASK_APP=wsgi.py && flask db upgrade
	@python seed.py
	@python seed_certificate_demo.py
