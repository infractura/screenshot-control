.PHONY: install test lint clean build docs serve

# Installation
install:
	pip install -e .

install-dev:
	pip install -r requirements-dev.txt

# Testing
test:
	pytest tests/ -v --cov=screenshot_control

# Linting
lint:
	pylint screenshot_control
	black screenshot_control --check

format:
	black screenshot_control

# Cleaning
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete

# Building
build:
	python setup.py sdist bdist_wheel

# Documentation
docs:
	mkdocs build

serve:
	uvicorn screenshot_control.server.main:app --reload --host 127.0.0.1 --port 8765

# Service management
service-install:
	sudo cp screenshot-api.service /etc/systemd/system/
	sudo systemctl daemon-reload
	sudo systemctl enable screenshot-api

service-start:
	sudo systemctl start screenshot-api

service-stop:
	sudo systemctl stop screenshot-api

service-status:
	sudo systemctl status screenshot-api

service-logs:
	sudo journalctl -u screenshot-api -f
