.ONESHELL:

# .DEFAULT_GOAL := run

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
PROJECT_NAME = News-Summarizer-Bot
PYTHON_INTERPRETER = python3

PYTHON_ENV = ./venv/Scripts/python3
PIP_ENV = ./venv/Scripts/pip

## Check if Python interpreter exists
ifeq (,$(shell which $(PYTHON_INTERPRETER)))
HAS_PYTHON=False
else
HAS_PYTHON=True
endif

#################################################################################
# COMMANDS                                                                      #
#################################################################################

# WINDOWS OS                                                                     
#################################################################################

ifeq ($(OS), Windows_NT)

# ## Run the main app
# run: venv	
# 	$(PYTHON_ENV) app.py

## Install Python Dependencies
requirements: test_environment
	$(PYTHON_ENV) -m pip install -U pip setuptools wheel
	$(PYTHON_ENV) -m pip install -r requirements.txt

## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Lint using flake8
lint:
	flake8 src

## Set up python interpreter environment
create_environment:
ifeq (True,$(HAS_PYTHON))
	$(PYTHON_INTERPRETER) -m venv venv
	@echo ">>> New virtualenv created. Activate with:\nmake activate_environment"
else
	@echo ">>> Python interpreter not found. Please install Python version 3 and above."
endif

## Activate the virtual environment
activate_environment:
ifeq (True,$(shell test -d venv && echo True))
	@echo ">>> Activating virtual environment. Run the following command:\nsource venv/bin/activate"
	source venv/bin/activate
else
	@echo ">>> Virtual environment not found. Please create it first by running:\nmake create_environment"
endif

## Test python environment is setup correctly
test_environment:
ifeq (True,$(shell test -d venv && echo True))
	$(PYTHON_ENV) test_environment.py
else
	@echo ">>> Virtual environment not found. Please create it first by running:\nmake create_environment"
endif

# LINUX/MAC OS AND OTHER OS                                                                     
#################################################################################

else
# TODO - add Linux/MacOS version of commands in all targets above

endif

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################




