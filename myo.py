import re
import time
from serial.tools.list_ports import comports
from bglib import BGLib
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
        print("Detecting available ports")
        for p in comports():
            if re.search(r'PID=2458:0*1', p[2]):
                print('Port detected: ', p[0])
                print()
                return p[0]
        return None

    def receive(self):
        self.lib.check_activity(self.serial)

    def send(self, msg):
        time.sleep(0.2)
        self.lib.send_command(self.serial, msg)

    def handle_discover(self, e, payload):
        if self.scanning and not self.myo_address:
            print("Device found", payload['sender'])
            if payload['data'].endswith(bytes(self.myo_id)):
                self.myo_address = payload['sender']
                print("Myo found", self.myo_address)
                print()
                self.scanning = False

    def handle_connect(self, e, payload):
        self.bluetoothConnectionID = payload['connection_handle']
        print("Connected with id", self.bluetoothConnectionID)

    def handle_disconnect(self, e, payload):
        print("Disconnected:", payload)

    def handle_connection_status(self, e, payload):
        print("Connection status: ", payload)
        self.connected = True

    def handle_emg(self, e, payload):
        emg_handles = [43, 46, 49, 52]
        if payload['atthandle'] in emg_handles and self.connected:
            print(list(payload['value']))

    def set_handlers(self):
        self.lib.ble_evt_gap_scan_response.add(self.handle_discover)
        self.lib.ble_rsp_gap_connect_direct.add(self.handle_connect)
        self.lib.ble_evt_attclient_attribute_value.add(self.handle_emg)
        self.lib.ble_evt_connection_disconnected.add(self.handle_disconnect)
        self.lib.ble_evt_connection_status.add(self.handle_connection_status)
        self.lib.ble_rsp_attclient_read_by_handle.add(print)
        # self.bglib.ble_rsp_attclient_attribute_write.add(print)

    def disconnect_all(self):
        self.send(self.lib.ble_cmd_gap_end_procedure())
        self.send(self.lib.ble_cmd_connection_disconnect(0))
        self.send(self.lib.ble_cmd_connection_disconnect(1))
        self.send(self.lib.ble_cmd_connection_disconnect(2))

    def connect(self):
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


if __name__ == '__main__':
    myo = Myo()
    myo.disconnect_all()
    myo.connect()
    print("Ready for EMG data")
    while True:
        myo.receive()
