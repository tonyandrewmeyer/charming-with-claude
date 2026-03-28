#!/bin/bash
# Redirect documentation.ubuntu.com to localhost for conditions C/D/E.
MARKER="# llms-txt-experiment"
if ! grep -q "${MARKER}" /etc/hosts; then
    echo "127.0.0.1 documentation.ubuntu.com ${MARKER}" | sudo tee -a /etc/hosts
    echo "Local docs enabled"
else
    echo "Local docs already enabled"
fi
