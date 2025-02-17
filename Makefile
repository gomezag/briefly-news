# Define variables
VENV_DIR := .venv
REQUIREMENTS_FILE := requirements-dev.txt
BRANCH ?= 'main'
LIMIT ?= 1
SITES ?= ultimahora,abc,lanacion,cincodias

# Define the name of the app and the Python file that contains the Dash app
APP_NAME = dash_app
APP_FILE = dashapp.app
PID_FILE = $(APP_NAME).pid

.PHONY: venv scrape embed doc clean deployvenv

# Create virtual environment and install dependencies
venv: clean
	@echo "Creating virtual environment..."
	@test -d $(VENV_DIR) || python -m venv $(VENV_DIR)
	. ./$(VENV_DIR)/bin/activate; \
		pip install -r $(REQUIREMENTS_FILE); \
		python -m spacy download es_core_news_md;
	@echo "Virtual environment created and requirements installed."

deployenv: clean
	@echo "Creating virtual environment..."
	@test -d $(VENV_DIR) || python -m venv $(VENV_DIR)
	. ./$(VENV_DIR)/bin/activate; \
		pip install -r requirements.txt; \
	  	echo "Virtual environment created and requirements installed.";


# Remove virtual environment directory
clean:
	@echo "Removing virtual environment directory..."
	@rm -rf $(VENV_DIR)

# Run pytest with additional arguments
test:
	. ./$(VENV_DIR)/bin/activate; \
		echo "Installing pytest..."; \
		pip install pytest; \
		echo "Running pytest with additional arguments: $(ARGS)"; \
		python -m pytest $(ARGS);

# Scrape data
scrape:
	. ./$(VENV_DIR)/bin/activate; \
		echo "Scraping to branch $(BRANCH)"; \
		python -m routines.scrape $(BRANCH) $(LIMIT) $(SITES);

embed:
	. ./$(VENV_DIR)/bin/activate; \
		export PYTHONPATH=$(CURDIR); \
		echo "Embedding articles"; \
		python -m routines.embed $(BRANCH) $(LIMIT);

tag:
	. ./$(VENV_DIR)/bin/activate; \
		export PYTHONPATH=$(CURDIR); \
		echo "Tagging articles"; \
		python -m routines.tag $(BRANCH) $(LIMIT);

frontend:
	@. ./$(VENV_DIR)/bin/activate; \
		if [ -f $(PID_FILE) ]; then \
			echo "Stopping app..."; \
			kill $$(cat $(PID_FILE)) > /dev/null 2> /dev/null; \
			rm $(PID_FILE); \
		fi; \
		echo "Starting app..."; \
		nohup python -m $(APP_FILE) > dash.log 2>&1 & echo $$! > $(PID_FILE); \
		echo "App started in http://localhost:8050"; \
		echo "To stop it, run make frontend-stop"

frontend-stop:
	@echo "Stopping app..."
	@kill $$(cat $(PID_FILE)) > /dev/null 2>/dev/null ||:
	@rm $(PID_FILE)


doc:
	@pip install pydoc-markdown==2.1.3
	@cd doc/ && pydocmd build
	@echo "Visit documentation in: file://$(PWD)/doc/_build/site/index.html"