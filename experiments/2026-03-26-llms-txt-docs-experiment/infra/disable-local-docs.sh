#!/bin/bash
# Restore normal DNS for documentation.ubuntu.com (conditions A/B).
sudo sed -i '/# llms-txt-experiment/d' /etc/hosts
echo "Local docs disabled — using real internet"
