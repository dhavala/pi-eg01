#!/usr/bin/env python3
"""
Simple LED control for Raspberry Pi 3.
Type 1 to turn LED on, 0 to turn off. Type q to quit.
"""

import RPi.GPIO as GPIO

# Configurable: BCM pin number (GPIO 17 = Physical Pin 11)
LED_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LED_PIN, GPIO.OUT)

print("LED Control - Enter 1 (on), 0 (off), or q (quit)")
print("Note: Run with sudo for GPIO access: sudo python3 led_control.py")
print("-" * 40)

try:
    while True:
        user_input = input("> ").strip().lower()
        if user_input == "q":
            break
        if user_input == "1":
            GPIO.output(LED_PIN, GPIO.HIGH)
            print("LED ON")
        elif user_input == "0":
            GPIO.output(LED_PIN, GPIO.LOW)
            print("LED OFF")
        else:
            print("Invalid input. Enter 1, 0, or q")
finally:
    GPIO.cleanup()
    print("\nGPIO cleaned up. Goodbye.")
