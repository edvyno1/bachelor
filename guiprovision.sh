#!/bin/bash
set -euxo pipefail

# Deps
sudo apt-get update --allow-releaseinfo-change

sudo apt-get install -y --no-install-recommends ubuntu-desktop
sudo apt-get install -y --no-install-recommends virtualbox-guest-utils virtualbox-guest-x11

# Libs
sudo apt-get -y install libcurl4-gnutls-dev libpam0g-dev dos2unix

# Python
sudo apt-get -y install python3-pip python3-flask

# Set up secondary user; salSp1wOPp6fk = encrypted 'test'
sudo useradd -m -p salSp1wOPp6fk test
sudo usermod -aG sudo test

find /vagrant -not -path "/vagrant/.vagrant/*" -type f -print0 | xargs -0 dos2unix -ic0 | xargs -0 dos2unix -b

sudo shutdown -r now