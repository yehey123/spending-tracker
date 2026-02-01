.PHONY: compile sync build up test lint hooks install

# Dependency Management
compile:
	pip install pip-tools
	python -m ensurepip --upgrade
	pip-compile requirements/base.in --output-file=requirements/base.txt
	pip-compile requirements/dev.in --output-file=requirements/dev.txt

sync:
	pip-sync base.txt dev.txt

install: compile sync

# Quality Control
hooks:
	pre-commit install && pre-commit install --hook-type pre-push

lint:
	ruff check . --fix

test:
	docker-compose run --rm backend pytest

# Docker related commands

check-docker:
	@echo "Checking Docker status..."
	@if ! docker info >/dev/null 2>&1; then \
		echo "Docker is not running. Launching Docker Desktop..."; \
		open -a Docker; \
		echo "Waiting for Docker to initialize..."; \
		until docker info >/dev/null 2>&1; do \
			printf "."; \
			sleep 2; \
		done; \
		echo "\nDocker is ready!"; \
	else \
		echo "Docker is already running."; \
	fi

build: check-docker install
	docker-compose build

up: check-docker
	docker-compose up -d