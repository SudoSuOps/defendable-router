SHELL := /bin/bash
VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
DR := $(VENV)/bin/defendablerouter
RUN := data/runs/router_smoke_001

.PHONY: install test smoke verify clean-runs clean

$(VENV)/bin/activate:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip wheel

install: $(VENV)/bin/activate
	$(PIP) install -e ".[dev]"

test: install
	$(VENV)/bin/pytest -q

smoke: install
	@rm -rf $(RUN)
	$(DR) receipt create --event defendablerouter/examples/sample_event.json --out $(RUN)
	$(DR) receipt verify --run $(RUN)
	$(DR) agent kimi-review --run $(RUN)
	@echo ""
	@echo "=== smoke complete ==="
	@cat $(RUN)/object_storage_path.txt

verify: install
	$(DR) receipt verify --run $(RUN)

clean-runs:
	rm -rf data/runs/*
	mkdir -p data/runs
	touch data/runs/.gitkeep

clean:
	rm -rf $(VENV) .pytest_cache **/__pycache__ *.egg-info build dist
