#!/bin/bash
set -euxo pipefail

# Deps
sudo apt-get update --allow-releaseinfo-change
sudo apt-get -y install libcurl4-gnutls-dev libpam0g-dev

# Python
sudo apt-get -y install python3-pip python3-flask