#!/bin/bash

sudo rm -r /server
sudo mkdir /server
sudo cp -r generated/ /server/generated

sudo cp generated/*.nginx /etc/nginx/sites-enabled/
sudo cp generated/*.nginx /etc/nginx/sites-available/
service nginx restart