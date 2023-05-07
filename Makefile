# Define variables
VENV_DIR := venv
REQUIREMENTS_FILE := requirements.txt
BRANCH ?= 'main'
LIMIT ?= 1

# Define the name of the app and the Python file that contains the Dash app
APP_NAME = dash_app
APP_FILE = dashapp.app
PID_FILE = $(APP_NAME).pid

.PHONY: venv scrape embed

# Create virtual environment and install dependencies
venv:
	@echo "Creating virtual environment..."
	@test -d $(VENV_DIR) || python -m venv $(VENV_DIR)
	@pip install -r $(REQUIREMENTS_FILE)
	@python -m spacy download es_core_news_md
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
	@if [ -f $(PID_FILE) ]; then \
  		echo "Stopping app..."; \
		kill $$(cat $(PID_FILE)); \
	fi
	@echo "Starting app..."
	@nohup python -m $(APP_FILE) > dash.log 2>&1 & echo $$! > $(PID_FILE)

frontend-stop:
	@echo "Stopping app..."
	@kill $$(cat $(PID_FILE))
	@rm $(PID_FILE)
