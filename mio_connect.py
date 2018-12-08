from src.myodriver import MyoDriver
from src.config import Config
import serial
import getopt
import sys


def main(argv):
    config = Config()
    try:
        opts, args = getopt.getopt(argv, 'hsn:a:p:v', ['help', 'shutdown', 'nmyo', 'address', 'port', 'verbose'])
    except getopt.GetoptError:
        sys.exit(2)
    turnoff = False
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print_usage()
            sys.exit()
        elif opt in ('-s', '--shutdown'):
            turnoff = True
        elif opt in ("-n", "--nmyo"):
            config.MYO_AMOUNT = int(arg)
        elif opt in ("-a", "--address"):
            config.OSC_ADDRESS = arg
        elif opt in ("-p", "--port"):
            config.OSC_PORT = arg
        elif opt in ("-v", "--verbose"):
            config.VERBOSE = True

    # Run
    myo_driver = None
    try:
        myo_driver = MyoDriver(config)
        myo_driver.run()
        if turnoff:
            myo_driver.deep_sleep_all()
            return
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
            if Config.DEEP_SLEEP_AT_KEYBOARD_INTERRUPT:
                myo_driver.deep_sleep_all()
            else:
                myo_driver.disconnect_all()


def print_usage():
    # TODO: Implement help message.
    print("[Help]")
    pass


if __name__ == "__main__":
    main(sys.argv[1:])
