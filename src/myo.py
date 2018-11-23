import re
import time
from serial.tools.list_ports import comports
from public.bglib import BGLib
import serial


class Myo:
    myo_id = [0x42, 0x48, 0x12, 0x4A,
              0x7F, 0x2C, 0x48, 0x47,
              0xB9, 0xDE, 0x04, 0xA9,
              0x01, 0x00, 0x06, 0xD5]

    def __init__(self):
        self.serial = serial.Serial(port=self._detect_port(), baudrate=9600, dsrdtr=1)
        self.lib = BGLib()

        self.myo_address = None
        self.bluetoothConnectionID = None
        self.scanning = False
        self.connected = False

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

    def receive(self):
        """
        Check for received evens and handle them.
        """
        self.lib.check_activity(self.serial)

    def send(self, msg):
        """
        Send given message through serial.
        :param msg: packed message to send
        """
        # A small delay is required for the Myo to process them correctly
        time.sleep(0.2)
        self.lib.send_command(self.serial, msg)

    def handle_discover(self, e, payload):
        """
        Handler for ble_evt_gap_scan_response event.
        """
        if self.scanning and not self.myo_address:
            print("Device found", payload['sender'])
            if payload['data'].endswith(bytes(self.myo_id)):
                self.myo_address = payload['sender']
                print("Myo found", self.myo_address)
                print()
                self.scanning = False

    def handle_connect(self, e, payload):
        """
        Handler for ble_rsp_gap_connect_direct event.
        """
        self.bluetoothConnectionID = payload['connection_handle']
        print("Connected with id", self.bluetoothConnectionID)

    def handle_disconnect(self, e, payload):
        """
        Handle for ble_evt_connection_disconnected event.
        """
        print("Disconnected:", payload)

    def handle_connection_status(self, e, payload):
        """
        Handler for ble_evt_connection_status event.
        """
        print("Connection status: ", payload)
        self.connected = True

    def handle_emg(self, e, payload):
        """
        Handler for EMG events, expected as a ble_evt_attclient_attribute_value event with handle 43, 46, 49 or 52.
        """
        emg_handles = [43, 46, 49, 52]
        if payload['atthandle'] in emg_handles and self.connected:
            print(list(payload['value']))

    def set_handlers(self):
        """
        Set handlers for relevant events.
        """
        self.lib.ble_evt_gap_scan_response.add(self.handle_discover)
        self.lib.ble_rsp_gap_connect_direct.add(self.handle_connect)
        self.lib.ble_evt_attclient_attribute_value.add(self.handle_emg)
        self.lib.ble_evt_connection_disconnected.add(self.handle_disconnect)
        self.lib.ble_evt_connection_status.add(self.handle_connection_status)
        self.lib.ble_rsp_attclient_read_by_handle.add(print)
        # self.bglib.ble_rsp_attclient_attribute_write.add(print)

    def disconnect_all(self):
        """
        Stop possible scanning and close all connections.
        """
        self.send(self.lib.ble_cmd_gap_end_procedure())
        self.send(self.lib.ble_cmd_connection_disconnect(0))
        self.send(self.lib.ble_cmd_connection_disconnect(1))
        self.send(self.lib.ble_cmd_connection_disconnect(2))

    def connect(self):
        """
        Procedure for connection with the Myo Armband. Scans, connects, disables sleep and starts EMG stream.
        """
        # Add handlers for expected events
        self.set_handlers()

        # Discover
        print("Scanning")
        self.send(self.lib.ble_cmd_gap_discover(1))

        # Await response
        self.scanning = True
        while self.myo_address is None:
            self.lib.check_activity(self.serial)

        # End gap
        self.send(self.lib.ble_cmd_gap_end_procedure())

        # Direct connection
        print("Connecting to", self.myo_address)
        self.send(self.lib.ble_cmd_gap_connect_direct(self.myo_address, 0, 6, 6, 64, 0))

        # Await response
        while self.bluetoothConnectionID is None or not self.connected:
            self.lib.check_activity(self.serial)

        # Notify successful connection with print and vibration
        print("Connection successful")
        print()
        self.send(self.lib.ble_cmd_attclient_attribute_write(self.bluetoothConnectionID, 0x0019, [0x03, 0x01, 0x01]))

        # Disable sleep
        self.send(self.lib.ble_cmd_attclient_attribute_write(self.bluetoothConnectionID, 0x0019, [0x09, 0x01, 0x01]))

        # Start EMG
        self.send(self.lib.ble_cmd_attclient_attribute_write(self.bluetoothConnectionID, 0x19,
                                                             [0x01, 0x03, 0x02, 0x01, 0x00]))

        # Subscribe for EMG
        self.send(self.lib.ble_cmd_attclient_attribute_write(self.bluetoothConnectionID, 0x2c, [0x01, 0x00]))
        self.send(self.lib.ble_cmd_attclient_attribute_write(self.bluetoothConnectionID, 0x2f, [0x01, 0x00]))
        self.send(self.lib.ble_cmd_attclient_attribute_write(self.bluetoothConnectionID, 0x32, [0x01, 0x00]))
        self.send(self.lib.ble_cmd_attclient_attribute_write(self.bluetoothConnectionID, 0x35, [0x01, 0x00]))

        # # Some useful read commands:
        # self.send(self.bglib.ble_cmd_attclient_read_by_handle(self.bluetoothConnectionID, 0x03))  # Read device name
        # self.send(self.bglib.ble_cmd_attclient_read_by_handle(self.bluetoothConnectionID, 0x17))  # Read firmware ver


if __name__ == '__main__':
    myo = None
    try:
        myo = Myo()
        myo.disconnect_all()
        myo.connect()
        print("Ready for EMG data")
        while True:
            myo.receive()
    except KeyboardInterrupt:
        pass
    except serial.serialutil.SerialException as err:
        print("Error opening port. Please close other programs using this serial.")
    finally:
        if myo is not None:
            myo.disconnect_all()
            print("\nDisconnected")
