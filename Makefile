# Define variables
VENV_DIR := venv
REQUIREMENTS_FILE := requirements.txt
BRANCH ?= 'main'
LIMIT ?= 1

# Define the name of the app and the Python file that contains the Dash app
APP_NAME = dash_app
APP_FILE = dashapp.app

.PHONY: venv scrape embed

# Create virtual environment and install dependencies
venv:
	@echo "Creating virtual environment..."
	@test -d $(VENV_DIR) || python -m venv $(VENV_DIR)
	@pip install -r $(REQUIREMENTS_FILE)
	@echo "Virtual environment created and requirements installed."

# Remove virtual environment directory
clean:
	@echo "Removing virtual environment directory..."
	@rm -rf $(VENV_DIR)

# Run pytest with additional arguments
test:
	@echo "Installing pytest..."
	@pip install pytest
	@echo "Running pytest with additional arguments: $(ARGS)"
	@python -m pytest $(ARGS)

# Scrape data
scrape:
	@echo "Scraping to branch $(BRANCH)"
	@python -m routines.scrape $(BRANCH) $(LIMIT)

embed:
	@export PYTHONPATH=$(CURDIR)
	@echo "Embedding articles"
	@python -m routines.embed $(BRANCH) $(LIMIT)

scrape-body:
	@python -m routines.scrape_body $(BRANCH) $(LIMIT)

frontend:
	@if [ -f $(APP_NAME).pid ]; then \
		echo "ERROR: $(APP_NAME) is already running (PID `cat $(APP_NAME).pid`)"; \
	else \
	  	python -m $(APP_FILE) & echo $$! > $(APP_NAME).pid; \
		echo "Started $(APP_NAME) (PID `cat $(APP_NAME).pid`)"; \
	fi

frontend-stop:
	@if [ -f $(APP_NAME).pid ]; then \
		kill `cat $(APP_NAME).pid`; \
		rm $(APP_NAME).pid; \
		echo "Stopped $(APP_NAME)"; \
	else \
		echo "ERROR: $(APP_NAME) is not running"; \
	fi