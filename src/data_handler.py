from pythonosc import udp_client
import struct


class DataHandler:
    def __init__(self, osc, config):
        self.osc = osc
        self.printEmg = config.PRINT_EMG
        self.printImu = config.PRINT_IMU

    def handle_emg(self, payload):
        """
        Handle EMG data.
        :param payload: emg data as two samples in a single pack.
        """
        if self.printEmg:
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
        if self.printImu:
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
