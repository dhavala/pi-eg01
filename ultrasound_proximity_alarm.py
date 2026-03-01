#!/usr/bin/env python3
"""
Ultrasound Proximity Alarm with Doppler-Effect Demo

Reads distance from HC-SR04 ultrasonic sensor. As an object gets closer:
  - LED turns ON when within threshold
  - Ambulance-like siren plays through external speaker (3.5mm jack / HDMI)
  - Siren amplitude (loudness) INCREASES as distance decreases

This demonstrates the Doppler-like effect: perceived intensity increases
as a source approaches. Connect an external speaker to the Raspberry Pi
audio output (3.5mm jack or HDMI) for the alarm sound.

Hardware: HC-SR04, LED, external speaker via Pi audio output
"""

import RPi.GPIO as GPIO
import time
import threading

try:
    import numpy as np
    import pyaudio
except ImportError:
    print("Required: pip install numpy pyaudio")
    print("On Raspberry Pi: sudo apt install python3-pyaudio; pip install numpy")
    exit(1)

# Pin configuration (BCM)
TRIGGER_PIN = 23
ECHO_PIN = 24
LED_PIN = 17

# Distance settings (cm)
DISTANCE_THRESHOLD_CM = 50   # Beyond this, no sound
MIN_VALID_DISTANCE_CM = 2    # Sensor minimum; treat as "very close"
MAX_VALID_DISTANCE_CM = 400  # Sensor max; treat as "far"

# Audio settings
SAMPLE_RATE = 44100
SIREN_FREQ_LOW = 800   # Hz - ambulance low tone
SIREN_FREQ_HIGH = 1100  # Hz - ambulance high tone
SIREN_CYCLE_SEC = 0.4  # Seconds per half-cycle (low->high or high->low)
CHUNK_SIZE = 1024      # Audio buffer size
MAX_AMPLITUDE = 0.4    # Max volume (0.0-1.0) to avoid distortion

# Shared state (protected by lock)
_amplitude = 0.0
_amplitude_lock = threading.Lock()
_stop_audio = False


def measure_distance_cm():
    """Send trigger pulse and measure echo duration. Returns distance in cm."""
    GPIO.output(TRIGGER_PIN, GPIO.LOW)
    time.sleep(0.00001)
    GPIO.output(TRIGGER_PIN, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIGGER_PIN, GPIO.LOW)

    timeout = time.time() + 0.02  # 20ms max wait
    while GPIO.input(ECHO_PIN) == GPIO.LOW:
        if time.time() > timeout:
            return MAX_VALID_DISTANCE_CM
    pulse_start = time.time()
    while GPIO.input(ECHO_PIN) == GPIO.HIGH:
        if time.time() > timeout:
            return MAX_VALID_DISTANCE_CM
    pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance_cm = pulse_duration * 17150
    return max(MIN_VALID_DISTANCE_CM, min(MAX_VALID_DISTANCE_CM, round(distance_cm, 2)))


def distance_to_amplitude(distance_cm):
    """
    Map distance to amplitude. Closer = louder (Doppler-like demo).
    Linear: at threshold (50cm) -> 0, at 0cm -> MAX_AMPLITUDE
    """
    if distance_cm > DISTANCE_THRESHOLD_CM:
        return 0.0
    # Closer distance -> higher amplitude
    # 0 cm -> 1.0, 50 cm -> 0.0
    fraction = 1.0 - (distance_cm / DISTANCE_THRESHOLD_CM)
    return MAX_AMPLITUDE * fraction


def generate_siren_chunk(state_ref, num_samples):
    """
    Generate one chunk of ambulance siren (alternating low/high tone).
    state_ref: [phase_radians, sample_counter] - mutable, for continuity
    Returns (samples, phase, sample_counter)
    """
    global _amplitude

    with _amplitude_lock:
        amp = _amplitude

    phase, sample_cnt = state_ref[0], state_ref[1]

    if amp <= 0:
        state_ref[1] = sample_cnt + num_samples
        return np.zeros(num_samples, dtype=np.float32), phase, sample_cnt + num_samples

    # Ambulance: alternate between low and high frequency
    half_cycle_samples = int(SAMPLE_RATE * SIREN_CYCLE_SEC / 2)
    cycle_len = 2 * half_cycle_samples
    indices = np.arange(num_samples) + sample_cnt
    cycle_pos = indices % cycle_len
    freq = np.where(cycle_pos < half_cycle_samples, SIREN_FREQ_LOW, SIREN_FREQ_HIGH)

    # Compute phase for each sample (integrate frequency)
    phase_deltas = 2 * np.pi * freq / SAMPLE_RATE
    phase_arr = np.cumsum(phase_deltas) + phase
    new_phase = float(phase_arr[-1])
    new_sample_cnt = sample_cnt + num_samples

    samples = amp * np.sin(phase_arr).astype(np.float32)
    state_ref[0], state_ref[1] = new_phase, new_sample_cnt
    return samples, new_phase, new_sample_cnt


def audio_thread_entry():
    """Background thread: streams ambulance siren with dynamic amplitude."""
    global _stop_audio
    p = pyaudio.PyAudio()
    try:
        stream = p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=SAMPLE_RATE,
            output=True,
            frames_per_buffer=CHUNK_SIZE,
        )
        state = [0.0, 0]  # [phase_radians, sample_counter]
        while not _stop_audio:
            chunk, _, _ = generate_siren_chunk(state, CHUNK_SIZE)
            stream.write(chunk.tobytes())
        stream.stop_stream()
        stream.close()
    except Exception as e:
        print("Audio error:", e)
    finally:
        p.terminate()


def main():
    global _amplitude, _stop_audio

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(TRIGGER_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)
    GPIO.setup(LED_PIN, GPIO.OUT)

    print("Ultrasound Proximity Alarm - Doppler-Effect Demo")
    print("=" * 50)
    print("As object gets CLOSER: siren gets LOUDER (amplitude increases)")
    print("Connect external speaker to Pi 3.5mm jack or HDMI")
    print("Press Ctrl+C to stop.")
    print("-" * 50)
    print("Run with sudo for GPIO: sudo python3 ultrasound_proximity_alarm.py")
    print("-" * 50)

    # Start audio thread
    audio_thread = threading.Thread(target=audio_thread_entry, daemon=True)
    audio_thread.start()

    try:
        while True:
            distance = measure_distance_cm()
            amp = distance_to_amplitude(distance)

            with _amplitude_lock:
                _amplitude = amp

            if distance <= DISTANCE_THRESHOLD_CM:
                GPIO.output(LED_PIN, GPIO.HIGH)
                status = "ON  | Siren: {:.0%} (object at {:.1f} cm)".format(
                    amp / MAX_AMPLITUDE, distance
                )
            else:
                GPIO.output(LED_PIN, GPIO.LOW)
                status = "OFF | Silent (object at {:.1f} cm)".format(distance)

            print("Distance: {:.1f} cm  LED: {}".format(distance, status))
            time.sleep(0.08)  # ~12 readings/sec

    except KeyboardInterrupt:
        pass
    finally:
        _stop_audio = True
        time.sleep(0.2)
        GPIO.output(LED_PIN, GPIO.LOW)
        GPIO.cleanup()
        print("\nStopped. GPIO cleaned up. Goodbye.")


if __name__ == "__main__":
    main()
