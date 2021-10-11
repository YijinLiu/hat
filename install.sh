#!/bin/bash

set -e

sudo apt install -y --no-install-recommends build-essential influxdb libgpiod2 python3-dev \
    python3-pip
sudo pip3 install --upgrade RPi.GPIO adafruit-circuitpython-dht gTTS influxdb paramiko
