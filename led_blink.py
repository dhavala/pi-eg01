#!/usr/bin/env python3
"""
LED Blink with configurable on/off cycle times.
User inputs on_cycle and off_cycle in seconds (e.g., 1,1 or 0.5,0.5).
Times are converted to milliseconds internally for precise timing.
Blinks in a loop until user presses Q and Enter.
"""

import RPi.GPIO as GPIO
import threading

# Configurable: BCM pin number (GPIO 17 = Physical Pin 11)
LED_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LED_PIN, GPIO.OUT)

print("LED Blink - Enter on and off cycle times in seconds (e.g., 1,1 or 0.5,0.5)")
print("Press Q and Enter to stop.")
print("Note: Run with sudo for GPIO access: sudo python3 led_blink.py")
print("-" * 40)

# Get user input for on/off times
while True:
    user_input = input("Enter on_time, off_time (seconds): ").strip()
    if user_input.lower() == "q":
        print("Exiting.")
        GPIO.cleanup()
        exit(0)
    try:
        parts = user_input.split(",")
        if len(parts) != 2:
            raise ValueError("Need two numbers separated by comma")
        on_seconds = float(parts[0].strip())
        off_seconds = float(parts[1].strip())
        if on_seconds < 0 or off_seconds < 0:
            raise ValueError("Times must be non-negative")
        break
    except ValueError as e:
        print(f"Invalid input: {e}. Example: 1,1 or 0.5,0.5")

# Convert seconds to milliseconds (stored internally)
on_ms = int(on_seconds * 1000)
off_ms = int(off_seconds * 1000)

print(f"Blinking: ON for {on_seconds}s ({on_ms}ms), OFF for {off_seconds}s ({off_ms}ms). Press Q + Enter to stop.")

stop_event = threading.Event()


def wait_for_quit():
    input()
    stop_event.set()


quit_thread = threading.Thread(target=wait_for_quit, daemon=True)
quit_thread.start()

try:
    while not stop_event.is_set():
        GPIO.output(LED_PIN, GPIO.HIGH)
        if stop_event.wait(timeout=on_ms / 1000.0):
            break
        GPIO.output(LED_PIN, GPIO.LOW)
        if stop_event.wait(timeout=off_ms / 1000.0):
            break
finally:
    GPIO.output(LED_PIN, GPIO.LOW)
    GPIO.cleanup()
    print("\nStopped. GPIO cleaned up. Goodbye.")
