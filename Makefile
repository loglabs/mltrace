.PHONY: help test run query scratch logrun server linecount
# include .env

# Makefile variables
VENV_NAME:=venv
PYTHON=${VENV_NAME}/bin/python3 

# Include your variables here
# AIRFLOW_HOME=~/.airflow

# Export environment variables
# VARS:=$(shell sed -ne 's/ *\#.*$$//; /./ s/=.*$$// p' .env )
# $(foreach v,$(VARS),$(eval $(shell echo export $(v)="$($(v))")))

.DEFAULT: help
help:
	@echo "make venv"
	@echo "       prepare development environment, use only once"
	@echo "make test"
	@echo "       run tests"

# Install dependencies whenever setup.py is changed.
venv: $(VENV_NAME)/bin/activate
$(VENV_NAME)/bin/activate: setup.py
	test -d $(VENV_NAME) || python3 -m venv $(VENV_NAME)
	${PYTHON} -m pip install -U pip
	${PYTHON} -m pip install -e .
	rm -rf ./*.egg-info
	touch $(VENV_NAME)/bin/activate

# lint: venv
# 	${PYTHON} -m pylint main.py

test: venv
	${PYTHON} -m pytest -s utils/tests.py

run: venv
	${PYTHON} populate_db.py

logrun: venv
	${PYTHON} populate_db_logging.py

query: venv
	${PYTHON} query.py

server: venv
	${PYTHON} -m flask run

linecount:
	find . -name "*.js" ! -path "*node_modules*" ! -path "./venv*" ! -path "./.git*" ! -path "./.vscode*" ! -path "*__pycache__*" ! -path "*.DS_Store" | xargs wc -l