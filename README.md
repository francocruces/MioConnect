# Background
MioConnect is a MyoConnect alternative for the Myo Armband, connects to the device(s) and transmits EMG/IMU via OSC.

This software was developed for the Emovere Project (http://www.emovere.cl/). They needed to avoid MyoConnect, because
they only required raw EMG/IMU data during a contemporary dance performance, and could not re-sync the armband after
sudden arm movements.

The code provides a comprehensible framework for a direct connection to the Myo Armband, using the Bluegiga BLE
Bluetooth library and the Myo Bluetooth Protocol released by Thalmic Labs on March 26, 2015. Hopefully this helps a lot
of people developing their own direct connections and understanding the bluetooth protocol.

# Requirements

This project runs on Python 3. Requirements are inside `requirements.txt` file.

* pyserial
* python-osc

You can easily install them via `pip install -r requirements.txt`.

# How to run
The file `mio_connect.py` contains the main loop for the application. Which instantiates a MyoDriver object and starts
the main procedure.

Run `mio_connect.py -h` to get help on the software usage. You can add the following commands:
* `-h` or `--help` to see this list
* `-s` or `--shutdown` to turn off (deep_sleep) the expected amount of myos
* `-n <amount>` or `-nmyo <amount>` to set the amount of devices to expect
* `-a <address>` or `-address <address>` to set OSC address
* `-p <port_number>` or `-port <port_number>` to set OSC port

Default configuration is written in a single file: `src/config.py`. These settings include:
* Amount of myos to detect
* EMG mode (send data, raw data, disabled, ...)
* IMU mode (send data, send events, disabled, ...)
* Classifier mode (enabled, disabled)
* Turn off (deep sleep) at KeyboardInterrupt
* Print EMG/IMU through console
* Verbose output
* Store and notify Myo Info after connections are made
* Added delay between messages sent to the armband

## What it does
The code is thoroughly documented and should be easy to follow, but a high-level description will be given:
* Sends a disconnect message in case some connections have persisted a previous connection
* Add handlers for every expected bluetooth event
* Starts a connection procedure for every expected armband
  * Discover devices
  * Find Myos
  * Establish a direct connection
  * Await answer for every critical event
  * Disable sleep
  * Start EMG/IMU/Classifier according to config file
  * Subscribe to EMG/IMU/Classifier events
* `set_handlers` method shows how every received message is handled. `handle_imu` and `handle_emg` are critical parts,
in which the OSC protocol is implemented
* An infinite loop lets the application listen for events 
* A keyboard interrupt (Ctrl+C) will trigger disconnect messages and end the program

# Project files

## `mio_connect.py`

This file contains the main loop for the application.

## `src`

* `config.py`: Settings for the application. Details under "How to run" section.
* `myo.py`: Class for a myo, handles device info and prints it nicely
* `myodriver.py`: Driver for myo connection and data handling.

## `src/public`

Contains files that are taken from another project following their respective licenses.

* `bglib.py`:  BGLib implementations for Bluegiga BLE112 Bluetooth Smart module.
* `myohw.py`: A partial transcription of myohw.h file released by Thalmic Labs Inc.


# Turn off Myo
The protocol provides the `deep_sleep` command (see `myohw`), according to the release notes, the armband will go into
a state with basically everything off and can stay in that state for months. The only way to turn it back on is plugging
it via USB (as MyoConnect would).

# Issues

* Not tested on Linux or OS X, but should work the same way.
* There's currently no way to enter Dongle name manually, if anything goes wrong, you should hardcode it at serial
initialization

# References
* Myo Bluetooth Protocol Release 
https://developerblog.myo.com/myo-bluetooth-spec-released/
Released by Thalmic Labs (2015).

* MyoStream
https://github.com/hcilab/MyoStream.
Its README.md file has an excellent explanation of the bluetooth protocol

* MyOSC
https://github.com/benkuper/MyOSC
OSC bridge for Myo.

* BGLib
https://github.com/jrowberg/bglib
BGLib implementations for Bluegiga BLE112 Bluetooth Smart module.