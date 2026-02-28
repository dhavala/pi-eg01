# Raspberry Pi 3 LED Control

Python applications for LED control via GPIO: manual on/off, configurable blink, and ultrasound proximity (HC-SR04) triggered LED.

## Hardware Wiring

Connect your LED to the Raspberry Pi as follows:

| Component | Connection |
|-----------|------------|
| GPIO 17 (BCM) / Physical Pin 11 | → 330Ω or 1kΩ resistor → LED anode (long leg) |
| GND (e.g., Physical Pin 6 or 9) | → LED cathode (short leg) |

```
Raspberry Pi 3          Breadboard
┌──────────────┐
│  GPIO 17     │────────[330Ω]──────(+) LED (-)────── GND
│  Pin 11      │
│              │
│  GND         │
└──────────────┘
```

**Tips:**
- Use a 330Ω–1kΩ resistor in series to limit current and protect the LED.
- LED anode (long leg) connects to the resistor; cathode (short leg) to GND.
- Use jumper wires between the Pi header and breadboard.

## Requirements

- Raspberry Pi 3 (or compatible)
- LED
- 330Ω or 1kΩ resistor
- Breadboard and jumper wires
- RPi.GPIO (pre-installed on Raspberry Pi OS)
- HC-SR04 ultrasonic sensor (for `ultrasound_led.py` only)

## Usage

### Basic LED control (`led_control.py`)

Run with `sudo` (required for GPIO access):

```bash
sudo python3 led_control.py
```

Then:
- Type `1` and Enter → LED turns **ON**
- Type `0` and Enter → LED turns **OFF**
- Type `q` and Enter (or Ctrl+C) → Exit and cleanup

### Blinking LED (`led_blink.py`)

```bash
sudo python3 led_blink.py
```

- Enter on and off cycle times in seconds, comma-separated (e.g., `1,1` or `0.5,0.5`)
- The LED blinks: on for the first value, off for the second, in a loop
- Times are converted to milliseconds internally
- Press `Q` and Enter to stop

### Ultrasound Proximity LED (`ultrasound_led.py`)

Uses an HC-SR04 ultrasonic sensor to detect objects. When an object is within **50 cm** of the sensor, the LED turns ON; otherwise it stays OFF.

**Ultrasound sensor wiring (HC-SR04):**

| Component      | Pi Connection                              |
| -------------- | ------------------------------------------ |
| Sensor VCC     | 5V (Physical Pin 2)                        |
| Sensor GND     | GND (Physical Pin 6 or 9)                  |
| Sensor Trigger | GPIO 23 (Physical Pin 16)                  |
| Sensor Echo    | GPIO 24 (Physical Pin 18)                  |
| LED            | GPIO 17 (Physical Pin 11) — same as above  |

**Note:** The HC-SR04 Echo pin outputs 5V. The Raspberry Pi GPIO is 3.3V tolerant. For safety, use a voltage divider (e.g., two 1kΩ resistors) between Echo and GPIO 24 to step down to ~2.5V.

```bash
sudo python3 ultrasound_led.py
```

- Runs until Ctrl+C
- Continuously measures distance and toggles LED based on 50 cm threshold
- Change `DISTANCE_THRESHOLD_CM` in the script to adjust the trigger distance

## Pin Configuration

| Pin  | BCM GPIO | Physical | Usage                        |
| ---- | -------- | -------- | ---------------------------- |
| LED  | 17       | 11       | LED output (all scripts)     |
| Trigger | 23    | 16       | HC-SR04 trigger (ultrasound) |
| Echo | 24       | 18       | HC-SR04 echo (ultrasound)    |

To use different pins, edit the constants at the top of the respective script.
