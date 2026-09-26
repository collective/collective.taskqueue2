# collective.taskqueue2 - developer tasks
#
# The development environment is managed by uv, there is no buildout anymore.
#
#   make dev       create the venv, create the Zope instance and start it
#   make fg        run the instance in the foreground (Ctrl-C to stop it)
#   make stop      stop the instance
#   make test      run the test suite
#   make coverage  run the test suite with a coverage gate of $(COVERAGE_MIN)%
#   make lint      run ruff
#   make help      list all targets

SHELL := /bin/bash

PLONE_VERSION   ?= 6.2
PLONE_RELEASE   ?= 6.2.2
PYTHON_VERSION  ?= 3.13

VENV            ?= .venv
PY              := $(VENV)/bin/python

CONSTRAINTS     ?= constraints-plone-$(PLONE_VERSION).txt
CONSTRAINTS_URL ?= https://dist.plone.org/release/$(PLONE_VERSION)-latest/constraints.txt

INSTANCE        ?= instance
INSTANCE_USER   ?= admin
INSTANCE_PASS   ?= admin
PORT            ?= 8080
SITE_ID         ?= Plone

ZOPE_INI        := $(INSTANCE)/etc/zope.ini
ZOPE_CONF       := $(INSTANCE)/etc/zope.conf
LOGFILE         := $(INSTANCE)/var/runwsgi.log
PIDFILE         := $(INSTANCE)/var/runwsgi.pid
RUN_PATTERN     := $(VENV)/bin/runwsgi $(ZOPE_INI)

# Environment of the dev instance. HUEY_CONSUMER=1 runs the queue consumer
# inside the instance, memory:// keeps the queue out of the filesystem.
HUEY_CONSUMER      ?= 1
HUEY_TASKQUEUE_URL ?= memory://
HUEY_LOG_LEVEL     ?= INFO
RUN_ENV = HUEY_CONSUMER=$(HUEY_CONSUMER) HUEY_TASKQUEUE_URL=$(HUEY_TASKQUEUE_URL) HUEY_LOG_LEVEL=$(HUEY_LOG_LEVEL)

COVERAGE_MIN    ?= 99

TEST_ARGS       ?=

.PHONY: help check-venv install dev instance site start stop restart status fg wait test coverage lint format build clean distclean

help: ## Show this help
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

$(VENV)/bin/python:
	uv venv --python $(PYTHON_VERSION) $(VENV)

check-venv: ## Recreate the venv if it was built with another Python version
	@if [ -x $(PY) ]; then \
		current=$$($(PY) -c "import sys; print('%d.%d' % sys.version_info[:2])"); \
		if [ "$$current" != "$(PYTHON_VERSION)" ]; then \
			echo "recreating $(VENV): Python $$current != $(PYTHON_VERSION)"; \
			rm -rf $(VENV); \
		fi; \
	fi

$(CONSTRAINTS):
	@echo "downloading $(CONSTRAINTS_URL)"
	curl --fail --location --show-error --output $@ $(CONSTRAINTS_URL)

install: check-venv $(VENV)/bin/python $(CONSTRAINTS) ## Create/refresh the venv and install the package
	uv pip install --python $(PY) -c $(CONSTRAINTS) "Plone==$(PLONE_RELEASE)"
	uv pip install --python $(PY) -c $(CONSTRAINTS) -e ".[test]"

dev: install site ## Set up everything and run the instance in the background
	@echo
	@echo "  Plone $(PLONE_RELEASE) is running on http://127.0.0.1:$(PORT)/$(SITE_ID)"
	@echo "  login: $(INSTANCE_USER) / $(INSTANCE_PASS)"
	@echo "  log:   $(LOGFILE)   (make fg for the foreground, make stop to stop it)"

instance: $(ZOPE_INI) ## Create the Zope WSGI instance (no-op if it exists)

$(ZOPE_INI): $(VENV)/bin/python
	$(VENV)/bin/mkwsgiinstance --dir $(INSTANCE) --user $(INSTANCE_USER):$(INSTANCE_PASS)
	@$(PY) -c "from pathlib import Path; p = Path('$(ZOPE_INI)'); \
		p.write_text(p.read_text().replace('127.0.0.1:8080', '127.0.0.1:$(PORT)'))"
	@echo "created $(ZOPE_INI) on port $(PORT)"

start: install instance ## Start the instance in the background (idempotent)
	@if pgrep -f "$(RUN_PATTERN)" > /dev/null; then \
		echo "instance already running (pid $$(pgrep -f '$(RUN_PATTERN)' | tr '\n' ' '))"; \
	else \
		$(RUN_ENV) nohup $(VENV)/bin/runwsgi $(ZOPE_INI) >> $(LOGFILE) 2>&1 & \
		echo $$! > $(PIDFILE); \
		echo "instance started (pid $$(cat $(PIDFILE)), log $(LOGFILE))"; \
	fi
	@$(MAKE) --no-print-directory wait

wait: ## Wait until the instance answers on http://127.0.0.1:$(PORT)/
	@for i in $$(seq 1 180); do \
		if curl --silent --fail --output /dev/null http://127.0.0.1:$(PORT)/; then \
			echo "instance is up after $${i}s"; exit 0; \
		fi; \
		sleep 1; \
	done; \
	echo "instance did not come up within 180s - see $(LOGFILE)"; exit 1

site: start ## Create the Plone site and install the add-on (idempotent)
	@status=$$(curl --silent --output /dev/null --write-out '%{http_code}' \
		--user $(INSTANCE_USER):$(INSTANCE_PASS) \
		--header "Accept: application/json" \
		http://127.0.0.1:$(PORT)/$(SITE_ID)); \
	if [ "$$status" = "200" ]; then \
		echo "site '$(SITE_ID)' already exists"; \
	else \
		echo "creating site '$(SITE_ID)'"; \
		curl --silent --fail --show-error \
			--user $(INSTANCE_USER):$(INSTANCE_PASS) --request POST \
			--header "Content-Type: application/json" \
			--header "Accept: application/json" \
			--data '{"site_id":"$(SITE_ID)","title":"$(SITE_ID)","description":"","default_language":"en","portal_timezone":"UTC"}' \
			http://127.0.0.1:$(PORT)/++api++/@sites/classic > /dev/null; \
	fi
	@status=$$(curl --silent --output /dev/null --write-out '%{http_code}' \
		--user $(INSTANCE_USER):$(INSTANCE_PASS) --request POST \
		--header "Accept: application/json" \
		http://127.0.0.1:$(PORT)/$(SITE_ID)/@addons/collective.taskqueue2/install); \
	if [ "$$status" = "204" ]; then echo "add-on installed"; \
	elif [ "$$status" = "400" ]; then echo "add-on already installed"; \
	else echo "installing the add-on failed (HTTP $$status)"; exit 1; fi
	@echo -n "taskqueue stats: "; \
		curl --silent --fail --user $(INSTANCE_USER):$(INSTANCE_PASS) \
			http://127.0.0.1:$(PORT)/$(SITE_ID)/@@taskqueue-stats; echo

stop: ## Stop the instance
	@if pgrep -f "$(RUN_PATTERN)" > /dev/null; then \
		pids=$$(pgrep -f "$(RUN_PATTERN)"); \
		kill $$pids; \
		for i in $$(seq 1 20); do \
			pgrep -f "$(RUN_PATTERN)" > /dev/null || break; \
			sleep 1; \
		done; \
		if pgrep -f "$(RUN_PATTERN)" > /dev/null; then kill -9 $$(pgrep -f "$(RUN_PATTERN)"); fi; \
		echo "instance stopped"; \
	else \
		echo "instance is not running"; \
	fi
	@rm -f $(PIDFILE)

restart: stop start ## Restart the instance

status: ## Report whether the instance is running
	@if pgrep -f "$(RUN_PATTERN)" > /dev/null; then \
		echo "running (pid $$(pgrep -f '$(RUN_PATTERN)' | tr '\n' ' '))"; \
	else \
		echo "not running"; \
	fi

fg: install instance ## Run the instance in the foreground
	$(RUN_ENV) $(VENV)/bin/runwsgi $(ZOPE_INI)

# Test suite, instrumented by coverage (shared by `test` and `coverage`).
TEST_RUN = COVERAGE_FILE=.coverage $(VENV)/bin/coverage run $(VENV)/bin/zope-testrunner --test-path=src -s collective.taskqueue2 --auto-color $(TEST_ARGS)

test: install ## Run the test suite and show the coverage report
	rm -f .coverage
	$(TEST_RUN) -v1
	$(VENV)/bin/coverage report -m

coverage: install ## Run the test suite and enforce $(COVERAGE_MIN)% coverage
	rm -f .coverage
	$(TEST_RUN)
	$(VENV)/bin/coverage report -m --fail-under=$(COVERAGE_MIN)

lint: install ## Run ruff
	$(VENV)/bin/ruff check src pyproject.toml

format: install ## Run ruff and apply its fixes
	$(VENV)/bin/ruff check --fix src pyproject.toml
	$(VENV)/bin/ruff format src

build: install ## Build the sdist and the wheel into dist/
	$(VENV)/bin/python -m build

clean: ## Remove the instance, coverage files and caches
	rm -rf $(INSTANCE) .coverage .coverage.* htmlcov dist build
	find src -name '__pycache__' -prune -exec rm -rf {} +
	find src -name '*.egg-info' -prune -exec rm -rf {} +

distclean: stop clean ## Also remove the venv
	rm -rf $(VENV)
