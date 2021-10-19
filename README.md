# kids-in-space

Educational Space Simulator for Children

Refer to https://www.instructables.com/Kids-In-Space-Space-Craft-Simulator/

# `kids-in-space.py`
* Cockpit - main cockpit visualisation
* PADD/Tricorder - tricorder is used to scan QR codes to learn more about elements

# Installation

Kids-in-Space requires python3 and runs on a rapsberry pi 2+. Install dependencies with

`pip3 -r requirements.txt`

# GameFlow

| State | Action | Tasks |
|---|---|---|
| 1 | Choose Planet | |
| 2 | Countdown | |
| 3 | Blast Off | |
| 4 | Flight | |
| 5 | Orbit | |
| 6 | Landing | |
| 7 | Exploration | Collect Chemicals (Elements, Molecules) |
| 8 | Goto 1 | |

# Lessons

TODO

# `proxy.py`

My Raspberry Pi is a model 2, which lacks Wi-Fi. Instead, it is connected directly to a laptop which runs this proxy to interface between the Raspberry Pi and other devices.

Note that this proxy is only supporting `GET` requests at this stage.
