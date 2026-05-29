#!/usr/bin/env bash
set -euo pipefail

APP_URL="${APP_URL:-https://defendable-router.fly.dev}"
APP_URL="${APP_URL%/}"

curl --fail --silent --show-error "${APP_URL}/health"
echo
curl --fail --silent --show-error "${APP_URL}/admin/summary"
echo
