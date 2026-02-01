#!/bin/bash
# Format file only if it's a Python file
if [[ "$1" == *.py ]]; then
    cd /home/ubuntu/beszel-operator
    uv run ruff format "$1"
fi