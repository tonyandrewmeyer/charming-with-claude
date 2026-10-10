#!/usr/bin/env bash
# RQ-6 issue/PR mining: alternates fetch (gh API) and classify (local) phases.
set -u
cd "$HOME/charm-research"
/usr/bin/timeout 900 /usr/bin/python3 rq6_issues.py
