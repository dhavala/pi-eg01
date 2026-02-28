#!/usr/bin/env python3
"""
Ultrasound Proximity LED Control

Reads distance from HC-SR04 ultrasonic sensor and turns the LED on when
an object is within 50 cm, off otherwise.
LED is on Physical Pin 11 (GPIO 17).
"""

import RPi.GPIO as GPIO
import time

# Pin configuration (BCM)
TRIGGER_PIN = 23
ECHO_PIN = 24
LED_PIN = 17
DISTANCE_THRESHOLD_CM = 50

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(TRIGGER_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)


def measure_distance_cm():
    """Send trigger pulse and measure echo duration. Returns distance in cm."""
    GPIO.output(TRIGGER_PIN, GPIO.LOW)
    time.sleep(0.00001)  # 10 us settle
    GPIO.output(TRIGGER_PIN, GPIO.HIGH)
    time.sleep(0.00001)  # 10 us pulse
    GPIO.output(TRIGGER_PIN, GPIO.LOW)

    # Wait for echo to go HIGH, then LOW
    while GPIO.input(ECHO_PIN) == GPIO.LOW:
        pass
    pulse_start = time.time()
    while GPIO.input(ECHO_PIN) == GPIO.HIGH:
        pass
    pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance_cm = pulse_duration * 17150  # 34300 / 2 (speed of sound, round-trip)
    return round(distance_cm, 2)


def main():
    print("Ultrasound Proximity LED - Object within 50 cm turns LED ON.")
    print("Press Ctrl+C to stop.")
    print("-" * 40)
    print("Run with sudo for GPIO access: sudo python3 ultrasound_led.py")
    print("-" * 40)

    try:
        while True:
            distance = measure_distance_cm()
            if distance <= DISTANCE_THRESHOLD_CM:
                GPIO.output(LED_PIN, GPIO.HIGH)
                status = "ON  (object within {:.1f} cm)".format(distance)
            else:
                GPIO.output(LED_PIN, GPIO.LOW)
                status = "OFF (object at {:.1f} cm)".format(distance)
            print("Distance: {:.1f} cm  LED: {}".format(distance, status))
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.output(LED_PIN, GPIO.LOW)
        GPIO.cleanup()
        print("\nStopped. GPIO cleaned up. Goodbye.")


if __name__ == "__main__":
    main()
