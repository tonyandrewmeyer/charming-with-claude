#!/usr/bin/env bash
# RQ-4 maintenance health: one daily batch (~60 repos) of gh API sampling.
set -u
cd "$HOME/charm-research"
/usr/bin/timeout 600 /usr/bin/python3 rq4_health.py
