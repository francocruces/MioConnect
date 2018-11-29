from src.public.myohw import *


class Myo:

    def __init__(self, address):
        self.address = address
        self.connectionId = None
        self.device_name = None
        self.firmware_version = None

    def set_id(self, connection_id):
        self.connectionId = connection_id
        return self

    def handle_attribute_value(self, payload):
        if self.connectionId == payload['connection']:
            if payload['atthandle'] == ServiceHandles.DeviceName:
                self.device_name = payload['value'].decode()
                # print("Device name", payload['value'].decode())
            elif payload['atthandle'] == ServiceHandles.FirmwareVersionCharacteristic:
                self.firmware_version = payload['value']
                # print("Firmware version", payload['value'])
                if not payload['value'] == b'\x01\x00\x05\x00\xb2\x07\x02\x00':
                    print("MYO WITH UNEXPECTED FIRMWARE, MAY NOT BEHAVE PROPERLY.", payload['value'])

    def ready(self):
        return self.address is not None and \
               self.connectionId is not None and \
               self.device_name is not None and \
               self.firmware_version is not None

    def __str__(self):
        return "Myo: " + str(self.device_name) + ", " + \
               "Connection: " + str(self.connectionId) + ", " + \
               "Address: " + str(self.address) + ", " + \
               "Firmware: " + str(self.firmware_version)
