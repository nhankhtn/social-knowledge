#!/bin/bash
# Run script for the application

cd "$(dirname "$0")"
uv run python -m src.app

