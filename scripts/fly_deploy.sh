#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f "pyproject.toml" || ! -d "defendable_router" ]]; then
  echo "error: run this script from the defendable-router repo root" >&2
  exit 1
fi

if [[ -x ".venv/bin/pytest" ]]; then
  .venv/bin/pytest
else
  pytest
fi

fly deploy
