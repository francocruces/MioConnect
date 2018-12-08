import re
import time
import serial
from serial.tools.list_ports import comports
import struct

from src.public.bglib import BGLib
from src.public.myohw import *
from src.myo import Myo
from pythonosc import udp_client


class MyoDriver:
    """
    Responsible for handling myo connections and messages.
    """

    def __init__(self, config):
        self.config = config
        self.serial = serial.Serial(port=self._detect_port(), baudrate=9600, dsrdtr=1)
        self.osc = udp_client.SimpleUDPClient(self.config.OSC_ADDRESS, self.config.OSC_PORT)
        print("OSC Address: " + str(self.config.OSC_ADDRESS))
        print("OSC Port: " + str(self.config.OSC_PORT))
        self.lib = BGLib()

        self.myos = []

        self.myo_to_connect = None
        self.scanning = False
        self.connected = False

        # Add handlers for expected events
        self.set_handlers()

    def _detect_port(self):
        """
        Detect COM port.
        :return: COM port with the expected ID
        """
        self.print_status("Detecting available ports")
        for p in comports():
            if re.search(r'PID=2458:0*1', p[2]):
                self.print_status('Port detected: ', p[0]) if self.config.VERBOSE else ""
                self.print_status()
                return p[0]
        return None

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
        time.sleep(self.config.MESSAGE_DELAY)
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

    def handle_discover(self, e, payload):
        """
        Handler for ble_evt_gap_scan_response event.
        """
        if self.scanning and not self.myo_to_connect:
            self.print_status("Device found", payload['sender'])
            if payload['data'].endswith(bytes(Final.myo_id)):
                if not self._has_paired_with(payload['sender']):
                    self.myo_to_connect = Myo(payload['sender'])
                    self.print_status("Myo found", self.myo_to_connect.address)
                    self.print_status()
                    self.scanning = False

    def _has_paired_with(self, address):
        for m in self.myos:
            if m.address == address:
                return True
        return False

    def handle_connect(self, e, payload):
        """
        Handler for ble_rsp_gap_connect_direct event.
        """
        if not payload['result'] == 0:
            raise RuntimeError

    def handle_disconnect(self, e, payload):
        """
        Handle for ble_evt_connection_disconnected event.
        """
        self.print_status("Disconnected:", payload)

    def handle_connection_status(self, e, payload):
        """
        Handler for ble_evt_connection_status event.
        """
        if payload['address'] == self.myo_to_connect.address and payload['flags'] == 5:
            # self.print_status("Connection status: ", payload)
            self.connected = True
            self.myo_to_connect.set_id(payload['connection'])
            self.print_status("Connected with id", self.myo_to_connect.connection_id)

    def handle_attribute_value(self, e, payload):
        """
        Handler for EMG events, expected as a ble_evt_attclient_attribute_value event with handle 43, 46, 49 or 52.
        """
        emg_handles = [
            ServiceHandles.EmgData0Characteristic,
            ServiceHandles.EmgData1Characteristic,
            ServiceHandles.EmgData2Characteristic,
            ServiceHandles.EmgData3Characteristic
        ]
        imu_handles = [
            ServiceHandles.IMUDataCharacteristic
        ]
        myo_handles = [
            ServiceHandles.DeviceName,
            ServiceHandles.FirmwareVersionCharacteristic,
            ServiceHandles.BatteryCharacteristic
        ]
        if payload['atthandle'] in emg_handles:
            self.handle_emg(payload)
        elif payload['atthandle'] in imu_handles:
            self.handle_imu(payload)
        else:
            for myo in self.myos:
                myo.handle_attribute_value(payload)
            if payload['atthandle'] not in myo_handles:
                self.print_status(e, payload)

    def handle_emg(self, payload):
        """
        Handle EMG data.
        :param payload: emg data as two samples in a single pack.
        """
        if self.config.PRINT_EMG:
            print("EMG", payload['connection'], payload['atthandle'], payload['value'])

        # Send first sample
        data = payload['value'][0:8]
        builder = udp_client.OscMessageBuilder("/myo/emg")
        builder.add_arg(str(payload['connection']), 's')
        for i in struct.unpack('ii', data):
            builder.add_arg(i, 'i')
        self.osc.send(builder.build())

        # Send second message
        data = payload['value'][8:16]
        builder = udp_client.OscMessageBuilder("/myo/emg")
        builder.add_arg(str(payload['connection']), 's')
        for i in data:
            builder.add_arg(i, 'i')
        self.osc.send(builder.build())

    def handle_imu(self, payload):
        """
        Handle IMU data.
        :param payload: imu data in a single byte array.
        """
        if self.config.PRINT_IMU:
            print("IMU", payload['connection'], payload['atthandle'], payload['value'])
        # Send orientation
        data = payload['value'][0:8]
        builder = udp_client.OscMessageBuilder("/myo/orientation")
        builder.add_arg(str(payload['connection']), 's')
        for i in struct.unpack('hhhh', data):
            builder.add_arg(i, 'f')
        self.osc.send(builder.build())

        # Send accelerometer
        data = payload['value'][8:14]
        builder = udp_client.OscMessageBuilder("/myo/accel")
        builder.add_arg(str(payload['connection']), 's')
        for i in struct.unpack('hhh', data):
            builder.add_arg(i, 'f')
        self.osc.send(builder.build())

        # Send gyroscope
        data = payload['value'][14:20]
        builder = udp_client.OscMessageBuilder("/myo/gyro")
        builder.add_arg(str(payload['connection']), 's')
        for i in struct.unpack('hhh', data):
            builder.add_arg(i, 'f')
        self.osc.send(builder.build())

    def set_handlers(self):
        """
        Set handlers for relevant events.
        """
        self.lib.ble_evt_gap_scan_response.add(self.handle_discover)
        self.lib.ble_rsp_gap_connect_direct.add(self.handle_connect)
        self.lib.ble_evt_attclient_attribute_value.add(self.handle_attribute_value)
        self.lib.ble_evt_connection_disconnected.add(self.handle_disconnect)
        self.lib.ble_evt_connection_status.add(self.handle_connection_status)
        # self.lib.ble_rsp_attclient_read_by_handle.add(self.print_status)
        # self.bglib.ble_rsp_attclient_attribute_write.add(self.print_status)

    def disconnect_all(self):
        """
        Stop possible scanning and close all connections.
        """
        self.send(self.lib.ble_cmd_gap_end_procedure())
        self.send(self.lib.ble_cmd_connection_disconnect(0))
        self.send(self.lib.ble_cmd_connection_disconnect(1))
        self.send(self.lib.ble_cmd_connection_disconnect(2))

    def add_myo_connection(self):
        """
        Procedure for connection with the Myo Armband. Scans, connects, disables sleep and starts EMG stream.
        """

        # Discover
        self.print_status("Scanning")
        self.send(self.lib.ble_cmd_gap_discover(1))

        # Await response
        self.scanning = True
        while self.myo_to_connect is None:
            self.lib.check_activity(self.serial)

        # End gap
        self.send(self.lib.ble_cmd_gap_end_procedure())

        # Direct connection
        self.print_status("Connecting to", self.myo_to_connect.address)
        self.send(self.lib.ble_cmd_gap_connect_direct(self.myo_to_connect.address, *Final.direct_connection_tail))

        # Await response
        while self.myo_to_connect.connection_id is None or not self.connected:
            self.lib.check_activity(self.serial)

        # Notify successful connection with self.print_status and vibration
        self.print_status("Connection successful. Setting up...")
        self.print_status()
        self.write_att(self.myo_to_connect.connection_id,
                       ServiceHandles.CommandCharacteristic,
                       [MyoCommand.myohw_command_vibrate,
                        0x01,
                        VibrationType.myohw_vibration_short])

        # Disable sleep
        self.write_att(self.myo_to_connect.connection_id,
                       ServiceHandles.CommandCharacteristic,
                       [MyoCommand.myohw_command_set_sleep_mode,
                        0x01,
                        SleepMode.myohw_sleep_mode_never_sleep])

        self.myos.append(self.myo_to_connect)
        print("Myo ready", self.myo_to_connect.connection_id, self.myo_to_connect.address)
        print()
        self.myo_to_connect = None
        self.scanning = False
        self.connected = False

    def get_info(self):
        """
        Send read attribute messages and await answer.
        """
        self.print_status("Getting myo info")
        self.print_status()
        for myo in self.myos:
            self.read_att(myo.connection_id,
                          ServiceHandles.DeviceName)
            self.read_att(myo.connection_id,
                          ServiceHandles.FirmwareVersionCharacteristic)
            self.read_att(myo.connection_id,
                          ServiceHandles.BatteryCharacteristic)
        while not self._myos_ready():
            self.receive()
        print("Myo list:")
        for myo in self.myos:
            print(" - " + str(myo))
        print()

    def _myos_ready(self):
        """
        :return: True if every myo has its data set, False otherwise.
        """
        for m in self.myos:
            if not m.ready():
                return False
        return True

    def run(self):
        """
        Main. Disconnects possible connections and starts as many connections as needed.
        :param myo_amount: amount of myos to detect before EMG/IMU stream starts.
        """
        self.disconnect_all()
        while len(self.myos) < self.config.MYO_AMOUNT:
            print("*** Connecting myo " + str(len(self.myos) + 1) + " out of " + str(self.config.MYO_AMOUNT) + " ***")
            print()
            self.add_myo_connection()

    def print_status(self, *args):
        """
        Printer function for VERBOSE support.
        """
        if self.config.VERBOSE:
            print(*args)

    def deep_sleep_all(self):
        print("Disconnecting...")
        for m in self.myos:
            self.write_att(m.connection_id,
                           ServiceHandles.CommandCharacteristic,
                           [MyoCommand.myohw_command_deep_sleep])
        print("Disconnected.")

    def enable_data_all(self):
        """
        Start EMG/IMJ/Classifier data and subscribe to their corresponding characteristic.
        """
        # TODO: Subscribe to classifier events.
        for m in self.myos:
            # Start EMG
            self.write_att(m.connection_id,
                           ServiceHandles.CommandCharacteristic,
                           [MyoCommand.myohw_command_set_mode,
                            0x03,
                            self.config.EMG_MODE,
                            self.config.IMU_MODE,
                            self.config.CLASSIFIER_MODE])

            # Subscribe for IMU
            self.write_att(m.connection_id,
                           ServiceHandles.IMUDataDescriptor,
                           Final.subscribe_payload)

            # Subscribe for EMG
            self.write_att(m.connection_id,
                           ServiceHandles.EmgData0Descriptor,
                           Final.subscribe_payload)
            self.write_att(m.connection_id,
                           ServiceHandles.EmgData1Descriptor,
                           Final.subscribe_payload)
            self.write_att(m.connection_id,
                           ServiceHandles.EmgData2Descriptor,
                           Final.subscribe_payload)
            self.write_att(m.connection_id,
                           ServiceHandles.EmgData3Descriptor,
                           Final.subscribe_payload)
        if self.config.VERBOSE:
            print("Data enabled for all myos according to config.")
