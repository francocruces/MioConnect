from serial.tools.list_ports import comports
import serial
from src.public.bglib import BGLib
import re
import time
from src.public.myohw import *


class Bluetooth:
    """
    Responsible for serial comm and message encapsulation.
    New commands can be added using myohw.py and following provided commands.
    """
    def __init__(self, message_delay):
        self.lib = BGLib()
        self.message_delay = message_delay
        self.serial = serial.Serial(port=self._detect_port(), baudrate=9600, dsrdtr=1)

    @staticmethod
    def _detect_port():
        """
        Detect COM port.
        :return: COM port with the expected ID
        """
        print("Detecting available ports")
        for p in comports():
            if re.search(r'PID=2458:0*1', p[2]):
                print('Port detected: ', p[0])
                print()
                return p[0]
        return None

##############################################################################
#                                  PROTOCOL                                  #
##############################################################################

    def receive(self):
        """
        Check for received evens and handle them.
        """
        self.lib.check_activity(self.serial)

    def send(self, msg):
        """
        Send given message through serial. A small delay is required for the Myo to process them correctly
        :param msg: packed message to send
        """
        time.sleep(self.message_delay)
        self.lib.send_command(self.serial, msg)

    def write_att(self, connection, atthandle, data):
        """
        Wrapper for code readability.
        """
        self.send(self.lib.ble_cmd_attclient_attribute_write(connection, atthandle, data))

    def read_att(self, connection, atthandle):
        """
        Wrapper for code readability.
        """
        self.send(self.lib.ble_cmd_attclient_read_by_handle(connection, atthandle))

    def disconnect_all(self):
        """
        Stop possible scanning and close all connections.
        """
        self.send(self.lib.ble_cmd_gap_end_procedure())
        self.send(self.lib.ble_cmd_connection_disconnect(0))
        self.send(self.lib.ble_cmd_connection_disconnect(1))
        self.send(self.lib.ble_cmd_connection_disconnect(2))


##############################################################################
#                                  COMMANDS                                  #
##############################################################################

    def gap_discover(self):
        self.send(self.lib.ble_cmd_gap_discover(1))

    def end_gap(self):
        self.send(self.lib.ble_cmd_gap_end_procedure())

    def direct_connect(self, myo_address):
        self.send(self.lib.ble_cmd_gap_connect_direct(myo_address, *Final.direct_connection_tail))

    def send_vibration(self, connection, vibration_type):
        self.write_att(connection,
                       ServiceHandles.CommandCharacteristic,
                       [MyoCommand.myohw_command_vibrate,
                        0x01,
                        vibration_type])

    def send_vibration_short(self, connection):
        self.write_att(connection,
                       ServiceHandles.CommandCharacteristic,
                       [MyoCommand.myohw_command_vibrate,
                        0x01,
                        VibrationType.myohw_vibration_short])

    def send_vibration_medium(self, connection):
        self.send_vibration(connection, VibrationType.myohw_vibration_medium)

    def send_vibration_long(self, connection):
        self.send_vibration(connection, VibrationType.myohw_vibration_long)

    def disable_sleep(self, connection):
        self.write_att(connection,
                       ServiceHandles.CommandCharacteristic,
                       [MyoCommand.myohw_command_set_sleep_mode,
                        0x01,
                        SleepMode.myohw_sleep_mode_never_sleep])

    def read_device_name(self, connection):
        self.read_att(connection, ServiceHandles.DeviceName)

    def read_firmware_version(self, connection):
        self.read_att(connection, ServiceHandles.FirmwareVersionCharacteristic)

    def read_battery_level(self, connection):
        self.read_att(connection, ServiceHandles.BatteryCharacteristic)

    def deep_sleep(self, connection):
        self.write_att(connection,
                       ServiceHandles.CommandCharacteristic,
                       [MyoCommand.myohw_command_deep_sleep])

    def enable_data(self, connection, config):
        # TODO: Subscribe to classifier events.

        # Start EMG
        self.write_att(connection,
                       ServiceHandles.CommandCharacteristic,
                       [MyoCommand.myohw_command_set_mode,
                        0x03,
                        config.EMG_MODE,
                        config.IMU_MODE,
                        config.CLASSIFIER_MODE])

        # Subscribe for IMU
        self.write_att(connection,
                       ServiceHandles.IMUDataDescriptor,
                       Final.subscribe_payload)

        # Subscribe for EMG
        self.write_att(connection,
                       ServiceHandles.EmgData0Descriptor,
                       Final.subscribe_payload)
        self.write_att(connection,
                       ServiceHandles.EmgData1Descriptor,
                       Final.subscribe_payload)
        self.write_att(connection,
                       ServiceHandles.EmgData2Descriptor,
                       Final.subscribe_payload)
        self.write_att(connection,
                       ServiceHandles.EmgData3Descriptor,
                       Final.subscribe_payload)


##############################################################################
#                                  HANDLERS                                  #
##############################################################################

    def add_scan_response_handler(self, handler):
        self.lib.ble_evt_gap_scan_response.add(handler)

    def add_connect_response_handler(self, handler):
        self.lib.ble_rsp_gap_connect_direct.add(handler)

    def add_attribute_value_handler(self, handler):
        self.lib.ble_evt_attclient_attribute_value.add(handler)

    def add_disconnected_handler(self, handler):
        self.lib.ble_evt_connection_disconnected.add(handler)

    def add_connection_status_handler(self, handler):
        self.lib.ble_evt_connection_status.add(handler)
