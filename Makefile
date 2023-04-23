# Define variables
VENV_DIR := venv
REQUIREMENTS_FILE := requirements.txt

.PHONY: venv

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

scrape:
    @python scrape.py