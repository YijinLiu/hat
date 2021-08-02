#!/usr/bin/env python3

import sys
import argparse
import time

import Adafruit_DHT
import RPi.GPIO as GPIO

from db import DB
import led

def celsius_to_fahrenheit(degrees_celsius: float) -> float:
    return (degrees_celsius * 9/5) + 32

def to_range(v: float, l: float, h: float, min_p: float, max_p: float) -> float:
    if v <= l:
        return min_p
    if v >= h:
        return max_p
    return (v - l) * (max_p - min_p) / (h - l) + min_p

def temperature_to_color(temperature: float, luminosity: float) -> (float, float, float):
    green = luminosity
    if temperature < 20:
        green = to_range(temperature, 16, 20, 0, luminosity)
    elif temperature > 24:
        green = to_range(temperature, 24, 28, luminosity, 0)
    return (to_range(temperature, 24, 40, 0, luminosity), green,
            to_range(temperature, 4, 20, luminosity, 0))

def humidity_to_color(humidity: float, luminosity: float) -> (float, float, float):
    green = luminosity
    if humidity < 30:
        green = to_range(humidity, 20, 30, 0, luminosity)
    elif humidity > 50:
        green = to_range(humidity, 50, 60, luminosity, 0)
    return (to_range(humidity, 10, 30, luminosity, 0), green,
            to_range(humidity, 50, 80, 0, luminosity))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--fahrenheit', help='output temperature in Fahrenheit', action='store_true')
    parser.add_argument(
        '-l', '--luminosity', action='store', type=float, choices=range(0, 100), default=50)
    args = parser.parse_args()

    db = DB()
    hum_led = led.RGB(36, 38, 40)
    temp_led = led.RGB(11, 13, 15)
    while True:
        try:
            humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 4)
        except RuntimeError as e:
            # GPIO access may require sudo permissions. Other RuntimeError exceptions may occur,
            # but are common. Just try again.
            print(f'RuntimeError: {e}')
            print('GPIO Access may need sudo permissions.')
            time.sleep(2.0)
            continue

        if not db.add_data(humidity, temperature):
            print('Failed to add data into DB.')
        if args.fahrenheit:
            print('Temp: {0:0.1f}°F, Humidity: {1:0.1f}%'.format(celsius_to_fahrenheit(temperature), humidity))
        else:
            print('Temp:{0:0.1f}°C, Humidity: {1:0.1f}%'.format(temperature, humidity))

        if args.luminosity > 0:
            r, g, b = humidity_to_color(humidity, args.luminosity)
            hum_led.set_color(r, g, b)
            r, g, b = temperature_to_color(temperature, args.luminosity)
            temp_led.set_color(r, g, b)

        time.sleep(2.0)

    db.close()
    GPIO.cleanup()

if __name__ == "__main__":
    main()
