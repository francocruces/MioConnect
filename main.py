from src.myodriver import MyoDriver
from src.config import Config
import serial

myo_driver = None
try:
    myo_driver = MyoDriver()
    myo_driver.run(Config.MYO_AMOUNT)
    if Config.GET_MYO_INFO:
        myo_driver.get_info()
    print("Ready for data")
    while True:
        myo_driver.receive()
except KeyboardInterrupt:
    pass
except serial.serialutil.SerialException as err:
    print("ERROR: Couldn't open port. Please close MyoConnect and any program using this serial port.")
finally:
    if myo_driver is not None:
        myo_driver.disconnect_all()
        print("Disconnected.")
