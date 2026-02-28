# Raspberry Pi 3 LED Control

A simple Python application that turns an LED on or off via GPIO, based on user input (1 = on, 0 = off).

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

## Pin Configuration

The default GPIO pin is **BCM 17** (Physical Pin 11). To use a different pin, edit `LED_PIN` at the top of `led_control.py` or `led_blink.py`.
