#!/bin/bash

set -e 

sudo apt install -y --no-install-recommends build-essential influxdb python3-dev python3-pip
sudo pip3 install --upgrade Adafruit_DHT RPi.GPIO influxdb
