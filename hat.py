#!/usr/bin/env python3

# Please follow https://pimylifeup.com/raspberry-pi-humidity-sensor-dht22/ to setup stuff.

import argparse
from datetime import datetime
import sys
import time

import RPi.GPIO as GPIO
import board
import adafruit_dht

from db import DB
import led
import voice

def celsius_to_fahrenheit(degrees_celsius: float) -> float:
    return (degrees_celsius * 9/5) + 32

def to_range(v: float, l: float, h: float, min_p: float, max_p: float) -> float:
    if v <= l:
        return min_p
    if v >= h:
        return max_p
    return (v - l) * (max_p - min_p) / (h - l) + min_p

def temperature_to_color(temperature: float, low: float, high: float,
                         luminosity: float) -> (float, float, float):
    green = luminosity
    if temperature < low:
        green = to_range(temperature, low - 4.0, low, 0, luminosity)
    elif temperature > high - 4.0:
        green = to_range(temperature, high - 4.0, high, luminosity, 0)
    return (to_range(temperature, high - 4.0, high + 12.0, 0, luminosity), green,
            to_range(temperature, low - 16.0, low, luminosity, 0))

def humidity_to_color(humidity: float, low: float, high: float,
                      luminosity: float) -> (float, float, float):
    green = luminosity
    if humidity < low:
        green = to_range(humidity, low - 10.0, low, 0, luminosity)
    elif humidity > high:
        green = to_range(humidity, high, high + 10.0, luminosity, 0)
    return (to_range(humidity, low - 20.0, low, luminosity, 0), green,
            to_range(humidity, high, high + 30.0, 0, luminosity))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', type=str, default='Kid Room',
        help='The name of the device.')
    parser.add_argument(
        '-f', '--fahrenheit', help='output temperature in Fahrenheit', action='store_true')
    parser.add_argument(
        '-l', '--luminosity', action='store', type=float, choices=range(0, 100), default=0)
    parser.add_argument('--data_dir', type=str, default='data',
        help='Dir for data and TTS mp3 files.')
    parser.add_argument('--warning_low_temperature', type=float, default=20.0,
        help='The low temperature to send audio warning.')
    parser.add_argument('--warning_high_temperature', type=float, default=28.0,
        help='The high temperature to send audio warning.')
    parser.add_argument('--warning_low_humidity', type=float, default=42.0,
        help='The low humidity to send audio warning.')
    parser.add_argument('--warning_high_humidity', type=float, default=52.0,
        help='The high humidity to send audio warning.')
    parser.add_argument('--speaker_host', type=str, default='localhost', help='Host to play TTS.')
    parser.add_argument('--speaker_port', type=int, default=22, help='Port to play TTS.')
    parser.add_argument('--speaker_username', type=str, default='', help='Username of speaker.')
    parser.add_argument('--speaker_password', type=str, default='', help='Password of speaker.')
    parser.add_argument('--min_speaker_silence_secs', type=int, default=600,
        help='Minimal silence seconds after playing a warning.')
    args = parser.parse_args()

    db = DB()

    if args.luminosity > 0:
        hum_led = led.RGB(36, 38, 40)
        temp_led = led.RGB(11, 13, 15)

    last_warning_ts = 0
    dht_device = adafruit_dht.DHT22(board.D4)
    count = 0
    while True:
        try:
            temperature = dht_device.temperature
            humidity = dht_device.humidity
        except RuntimeError as e:
            # GPIO access may require sudo permissions. Other RuntimeError exceptions may occur,
            # but are common. Just try again.
            print(f'RuntimeError: {e}')
            print('GPIO Access may need sudo permissions.')
            time.sleep(2.0)
            continue

        if not db.add_data(humidity, temperature):
            print('Failed to add data into DB.')

        print('[{0} {1:08d}] Temperature: {2:0.1f}°F, Humidity: {3:0.1f}%'.format(
            datetime.now().strftime("%Y/%m/%d %H:%M:%S"), count,
            celsius_to_fahrenheit(temperature) if args.fahrenheit else temperature, humidity))

        if args.luminosity > 0:
            r, g, b = temperature_to_color(temperature, args.warning_low_temperature,
                args.warning_high_temperature, args.luminosity)
            temp_led.set_color(r, g, b)
            r, g, b = humidity_to_color(humidity, args.warning_low_humidity,
                args.warning_high_humidity, args.luminosity)
            hum_led.set_color(r, g, b)

        if args.speaker_host and time.time() - last_warning_ts >= args.min_speaker_silence_secs:
            try:
                if count % 2 == 0:
                    if temperature < args.warning_low_temperature:
                        voice.gtts_remote(f'{args.name} temperature {temperature} is too low.',
                            args.data_dir, args.speaker_host, args.speaker_port,
                            args.speaker_username, args.speaker_password)
                        last_warning_ts = time.time()
                    elif temperature > args.warning_high_temperature:
                        voice.gtts_remote(f'{args.name} temperature {temperature} is too high.',
                            args.data_dir, args.speaker_host, args.speaker_port,
                            args.speaker_username, args.speaker_password)
                        last_warning_ts = time.time()
                else:
                    if humidity < args.warning_low_humidity:
                        voice.gtts_remote(f'{args.name} humidity {humidity} is too low.',
                            args.data_dir, args.speaker_host, args.speaker_port,
                            args.speaker_username, args.speaker_password)
                        last_warning_ts = time.time()
                    elif temperature > args.warning_high_temperature:
                        voice.gtts_remote(f'{args.name} humidity {humidity} is too high.',
                            args.data_dir, args.speaker_host, args.speaker_port,
                            args.speaker_username, args.speaker_password)
                        last_warning_ts = time.time()
            except Exception as e:
                print(e)

        count += 1
        time.sleep(2.0)

    db.close()
    GPIO.cleanup()

if __name__ == "__main__":
    main()
