class Myo:

    def __init__(self, address):
        self.address = address
        self.connectionId = None

    def set_id(self, connection_id):
        self.connectionId = connection_id
