# CandyBot

CandyBot is a voice-controlled candy dispenser built around a Raspberry Pi. A user
asks for sweets out loud, in Catalan or Spanish, and the robot serves the requested
colours and amounts. It also refills itself: a rotating tray feeds candies past a
camera one by one, reads each colour, and drops it into the matching container.

The robot works with Skittles, sorted into five colours (red, orange, yellow, green
and purple). It was developed for the Robotics Lab (RLP) course at the Universitat
Autònoma de Barcelona.

## Motivation

Beyond being a fun machine, CandyBot is designed with children on the autism spectrum in mind.
We have a research ongoing about the topic and will give further details soon.

## How it works

1. The user turns the crank. A magnet sweeps past a reed switch, and those pulses
   tell the Pi the user is active, so recording starts.
2. When the crank stops, recording stops and the audio clip is sent to the CandyBot API.
3. The API transcribes the speech and turns it into a structured command: an action
   (dispense, reload or cancel) and a list of colours with quantities.
4. The Pi acts on it, dispensing the requested candies or running the self-sorting
   refill routine, and shows progress on the LCD screen.

Stock is tracked locally in a SQLite database, so the robot knows what it holds and
declines requests it cannot fulfil.

## Repository layout

```
BotSoftware/   Code that runs on the Raspberry Pi
Api/           Cloud service: speech-to-text + language model (FastAPI)
HW tests/      Standalone scripts to check each hardware part on its own
3D Models/     Printable parts (.stl) for the chassis and mechanism
```

The printable parts are still being finalised and will be added to `3D Models/`.

## Hardware

- Raspberry Pi 4
- Raspberry Pi Camera Module v2
- PCA9685 16-channel PWM driver (I2C)
- 5 SG90 servos, one per colour container (the dispensers)
- 1 SG90 servo for the directional ramp
- 1 continuous-rotation servo for the sorting tray
- 16x2 character LCD display with a PCF8574 I2C backpack
- USB sound card with an electret microphone
- Reed switch and a magnet, mounted on the crank

The default addresses and pins are defined in `BotSoftware/config/servo_config.py` and
in each controller; verify them against your own build:

- PCA9685 on I2C address `0x40`. Dispenser servos use channels 0 to 4
  (green, purple, red, orange, yellow). The ramp and tray channels are assigned
  during assembly.
- LCD on I2C address `0x3F`.
- Reed switch on GPIO 17 (BCM).
- Microphone as ALSA device `plughw:1,0` (find yours with `arecord -l`).
- Camera through the standard Pi camera port, read with `rpicam-still`.

## The API

The API is a small FastAPI service deployed on Google Cloud Run that turns a voice
clip into a structured command. It uses two Google Cloud services:

- Speech-to-Text (v2) for transcription, configured for Catalan (`ca-ES`).
- Vertex AI (Gemini 2.5 Flash) to read the transcript and emit strict JSON.

It exposes a single endpoint, `POST /v1/command`, which takes a WAV file and returns:

```json
{ "action": "dispense", "confidence": 0.95, "items": [ { "color": "red", "quantity": 2 } ] }
```

Requests are authenticated with a shared token in the `X-API-Token` header.

To run the service you need a Google Cloud project with Speech-to-Text and Vertex AI
enabled, and credentials available to it. It is configured through environment
variables: `GCP_PROJECT`, `GCP_LOCATION` (default `europe-west1`) and `API_TOKEN`.
The service is containerised (`Api/Dockerfile`) and its dependencies are managed with
Poetry (`Api/pyproject.toml`).

## Running the robot

The Pi side is meant to be simple: set two values and run one command.

You need a Raspberry Pi with Python 3, the hardware connected, and the Python
packages it relies on (`requests`, `python-dotenv`, `gpiozero`, `adafruit-servokit`,
`RPLCD`, and OpenCV for the camera). `arecord` and `rpicam-still` come with
Raspberry Pi OS.

Create a `.env` file inside `BotSoftware/` with the address of your deployed API and
the matching token:

```
API_URL=https://<your-cloud-run-url>/v1/command
API_TOKEN=<the same token configured in the API>
```

Then start the robot:

```
python -m BotSoftware.main
```

This runs the main loop: turn the crank, speak, and the robot serves or refills.

Before a full run, each subsystem can be checked on its own:

```
python "HW tests/test_palanca.py"                    # crank / reed switch
python "HW tests/test_ordenar.py"                    # sorting: tray, camera, ramp
python -m BotSoftware.controllers.servo_controller   # dispense one of each colour
```

If a piece of hardware is missing, the matching module prints a "no hardware" notice
and keeps running in a safe simulation mode, so the software can be developed and
tested away from the robot.

## Team

See [Roles.md](Roles.md).
