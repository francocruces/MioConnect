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
* `-s` or `--shutdown` to turn off (deep sleep) the expected amount of myos
* `-n <amount>` or `--nmyo <amount>` to set the amount of devices to expect
* `-a <address>` or `--address <address>` to set OSC address
* `-p <port_number>` or `--port <port_number>` to set OSC port
* `-v` or `--verbose` for verbose output

Default configuration is written in a single file: `src/config.py`. These settings include:
* `MYO_AMOUNT`: Default amount of myos to detect
* `EMG_MODE`: EMG mode (send data, raw data, disabled, ...)
* `IMU_MODE`: IMU mode (send data, send events, disabled, ...)
* `CLASSIFIER_MODE`: Classifier mode (enabled, disabled)
* `DEEP_SLEEP_AT_KEYBOARD_INTERRUPT`: Turn off (deep sleep) at KeyboardInterrupt
* `PRINT_EMG`: Print EMG/IMU through console
* `PRINT_IMU`: Verbose output
* `GET_MYO_INFO`: Store and notify Myo Info after connections are made
* `MESSAGE_DELAY`: Added delay between messages sent to the armband
* `RETRY_CONNECTION_AFTER`: Time to wait before retrying the connection after unexpected disconnect
* `MAX_RETRIES`: Maximum amount of retries before giving up

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

If a myo disconnects, an event is received and a reconnection routine will start with provided configuration.

# Project files

## `mio_connect.py`

This file contains the main loop for the application.

## `src`

Each file contains a single python class with its own responsibility:

* `bluetooth.py` / `Bluetooth(msg_delay)`: Serial communication and command encapsulation. Every command sent to the
armband should pass through this class. New commands can be added at the end of the command section, following the
structure of the other commands and reading the `myohw` file (the `.py` or the official one).

* `config.py` / `Config()`: Settings for the application. Details under "How to run" section.

* `data_handler.py` / `DataHandler(config_obj)`: Handles EMG/IMU data and sends it through OSC. Here lies encapsulated
the OSC message structure and no other file should change when adjusting it.
 
* `myo.py` / `Myo(address)`: Class for a myo, handles device info and prints it nicely. It's instantiated after the
address is received, and it's used inside handlers in order to properly connect/reconnect. It also keeps the data
obtained through MyoDriver's method `get_info()` (i.e. device name, battery level and firmware version), printing a Myo
object will display all the info.

* `myodriver.py` / `MyoDriver(config_obj)`: Driver for myo connection and data handling. Implements main procedures for
global functionality, such as connection and reconnection protocols and data/event handling.

## `src/public`

Contains files that are taken from another project following their respective licenses.

* `bglib.py`:  BGLib implementations for Bluegiga BLE112 Bluetooth Smart module.

* `myohw.py`: A partial transcription of myohw.h file released by Thalmic Labs Inc.


# Turn off Myo
The protocol provides the `deep_sleep` command (see `myohw`), according to the release notes, the armband will go into
a state with basically everything off and can stay in that state for months. The only way to turn it back on is plugging
it via USB (as MyoConnect would).

You can start a procedure for finding devices and the turning them all off with the `-s` (`--shutdown`) command. Using
it with `-n <amount>` will find and turn off given amount of myos.

# Issues

* Not tested on Linux or OS X, but should work the same way.
* There's currently no way to enter Dongle name manually, if anything goes wrong, you should hardcode it at serial
initialization.
* No user interface.
* Does not subscribe to Classifier events.

# Thalmic Labs rebrand

Thalmic Labs is no longer selling Myo Armbands and has their website (https://www.myo.com/) is now unreachable. The
developer forums (https://developer.thalmic.com/forums/) are also down and we should not expect any future support from
Thalmic, but the community may gather in another website (maybe https://www.reddit.com/r/thalmic/)

This is actually a rebrand, they have become "North" and released Smart Glasses powered by Alexa (website:
https://www.bynorth.com/).

Details here
https://venturebeat.com/2018/10/23/thalmic-labs-rebrands-as-north-launches-999-alexa-powered-holographic-glasses/.

# References
* Myo Bluetooth Protocol Release 
https://developerblog.myo.com/myo-bluetooth-spec-released/
Released by Thalmic Labs (2015).

* MyoStream
https://github.com/hcilab/MyoStream
Its README.md file has an excellent explanation of the bluetooth protocol.

* MyOSC
https://github.com/benkuper/MyOSC
OSC bridge for Myo.

* BGLib
https://github.com/jrowberg/bglib
BGLib implementations for Bluegiga BLE112 Bluetooth Smart module.

* About Thalmic Labs rebrand
https://venturebeat.com/2018/10/23/thalmic-labs-rebrands-as-north-launches-999-alexa-powered-holographic-glasses/
