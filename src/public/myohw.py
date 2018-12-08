"""
Copyright (c) 2015 Thalmic Labs Inc.
All rights reserved.

Redistribution and use in source and binary forms with or without
modification are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the copyright holder(s) nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES INCLUDING BUT NOT LIMITED TO THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER(S) BE LIABLE FOR ANY
DIRECT INDIRECT INCIDENTAL SPECIAL EXEMPLARY OR CONSEQUENTIAL DAMAGES
(INCLUDING BUT NOT LIMITED TO PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE DATA OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY WHETHER IN CONTRACT STRICT LIABILITY OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

"""
This code is a partial transcription of myohw.h file released by Thalmic Labs Inc.
https://github.com/thalmiclabs/myo-bluetooth/blob/master/myohw.h
"""


class Final:

    myo_id = [0x42, 0x48, 0x12, 0x4A,
              0x7F, 0x2C, 0x48, 0x47,
              0xB9, 0xDE, 0x04, 0xA9,
              0x01, 0x00, 0x06, 0xD5]

    direct_connection_tail = (0, 6, 6, 64, 0)

    subscribe_payload = [0x01, 0x00]


class Services:
    ControlService = 0x0001  # Myo info service
    MyoInfoCharacteristic = 0x0101  # Serial number for this Myo and various parameters which are specific to this
    # firmware. Read - only attribute.
    FirmwareVersionCharacteristic = 0x0201  # Current firmware  characteristic.
    CommandCharacteristic = 0x0401  # Issue commands to the Myo.Write - only characteristic.

    ImuDataService = 0x0002  # IMU service
    IMUDataCharacteristic = 0x0402
    MotionEventCharacteristic = 0x0502

    ClassifierService = 0x0003  # Classifier event service.
    ClassifierEventCharacteristic = 0x0103  # Classifier event data.Indicate - only characteristic.

    EmgDataService = 0x0005  # Raw EMG data service.
    EmgData0Characteristic = 0x0105  # Raw EMG data.Notify - only characteristic.
    EmgData1Characteristic = 0x0205  # Raw EMG data.Notify - only characteristic.
    EmgData2Characteristic = 0x0305  # Raw EMG data.Notify - only characteristic.
    EmgData3Characteristic = 0x0405  # Raw EMG data.Notify - only characteristic.


class ServiceHandles:
    """
    Thanks to https://github.com/brokenpylons/MyoLinux/blob/master/src/myoapi_p.h
    """
    # ControlService
    MyoInfoCharacteristic = 0x0
    DeviceName = 0x3
    BatteryCharacteristic = 0x11
    BatteryDescriptor = 0x12
    FirmwareVersionCharacteristic = 0x17
    CommandCharacteristic = 0x19

    # ImuDataService
    IMUDataCharacteristic = 0x1c
    IMUDataDescriptor = 0x1d
    # MotionEventCharacteristic

    # ClassifierService
    ClassifierEventCharacteristic = 0x0023

    EmgData0Characteristic = 0x2b
    EmgData1Characteristic = 0x2e
    EmgData2Characteristic = 0x31
    EmgData3Characteristic = 0x34

    EmgData0Descriptor = 0x2c
    EmgData1Descriptor = 0x2f
    EmgData2Descriptor = 0x32
    EmgData3Descriptor = 0x35


class StandardServices:
    BatteryService = 0x180f  # Battery service
    BatteryLevelCharacteristic = 0x2a19  # Current battery level information. Read/notify characteristic.
    DeviceName = 0x2a00  # Device name data. Read/write characteristic.


class Pose:
    myohw_pose_rest = 0x0000
    myohw_pose_fist = 0x0001
    myohw_pose_wave_in = 0x0002
    myohw_pose_wave_out = 0x0003
    myohw_pose_fingers_spread = 0x0004
    myohw_pose_double_tap = 0x0005
    myohw_pose_unknown = 0xffff


class MyoCommand:
    # payload size = 3: EmgMode ImuMode ClassifierMode
    myohw_command_set_mode = 0x01  # Set EMG and IMU modes.

    # payload size = 1: VibrationType
    myohw_command_vibrate = 0x03  # Vibrate.

    # payload size = 0
    myohw_command_deep_sleep = 0x04  # Put Myo into deep sleep.

    # payload size = 18: [duration strength]*
    myohw_command_vibrate2 = 0x07  # Extended vibrate.

    # payload size = 1: SleepMode
    myohw_command_set_sleep_mode = 0x09  # Set sleep mode.

    # payload size = 1: UnlockType
    myohw_command_unlock = 0x0a  # Unlock Myo.

    # payload size = 1: UserActionType
    myohw_command_user_action = 0x0b  # Notify user that an action has been recognized or confirmed


class EmgMode:
    myohw_emg_mode_none = 0x00  # Do not send EMG data.
    myohw_emg_mode_send_emg = 0x02  # Send filtered EMG data.
    myohw_emg_mode_send_emg_raw = 0x03  # Send raw (unfiltered) EMG data.


class ImuMode:
    myohw_imu_mode_none = 0x00  # Do not send IMU data or events.
    myohw_imu_mode_send_data = 0x01  # Send IMU data streams (accelerometer gyroscope and orientation).
    myohw_imu_mode_send_events = 0x02  # Send motion events detected by the IMU (e.g. taps).
    myohw_imu_mode_send_all = 0x03  # Send both IMU data streams and motion events.
    myohw_imu_mode_send_raw = 0x04  # Send raw IMU data streams.


class ClassifierMode:
    myohw_classifier_mode_disabled = 0x00  # Disable and reset the internal state of the onboard classifier.
    myohw_classifier_mode_enabled = 0x01  # Send classifier events (poses and arm events).


class VibrationType:
    myohw_vibration_none = 0x00  # Do not vibrate.
    myohw_vibration_short = 0x01  # Vibrate for a short amount of time.
    myohw_vibration_medium = 0x02  # Vibrate for a medium amount of time.
    myohw_vibration_long = 0x03  # Vibrate for a long amount of time.


class SleepMode:
    myohw_sleep_mode_normal = 0  # Normal sleep mode; Myo will sleep after a period of inactivity.
    myohw_sleep_mode_never_sleep = 1  # Never go to sleep.


class UnlockType:
    myohw_unlock_lock = 0x00  # Re-lock immediately.
    myohw_unlock_timed = 0x01  # Unlock now and re-lock after a fixed timeout.
    myohw_unlock_hold = 0x02  # Unlock now and remain unlocked until a lock command is received.


class UserActionType:
    myohw_user_action_single = 0  # User did a single discrete action such as pausing a video.

