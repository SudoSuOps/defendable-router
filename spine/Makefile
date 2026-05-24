SHELL := /bin/bash
VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
DR := $(VENV)/bin/defendablerouter
RUN := data/runs/router_smoke_001

.PHONY: install test smoke verify serve api-smoke clean-runs clean

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

serve: install
	$(DR) serve --host 0.0.0.0 --port 8080

api-smoke: install
	@echo "=== POST /intake/streetchat ==="
	@curl -sf -X POST http://localhost:8080/intake/streetchat \
	  -H "Content-Type: application/json" \
	  --data @defendablerouter/examples/sample_event.json | python3 -m json.tool

clean-runs:
	rm -rf data/runs/*
	mkdir -p data/runs
	touch data/runs/.gitkeep

clean:
	rm -rf $(VENV) .pytest_cache **/__pycache__ *.egg-info build dist
