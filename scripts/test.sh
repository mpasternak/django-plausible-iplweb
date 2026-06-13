#!/usr/bin/env bash

set -ex

uv run pytest --verbose --cov plausible/ --cov-report term --cov-report html tests/

uv run ruff check plausible tests

uv run ruff format --check plausible tests || true

uv run mypy plausible tests
