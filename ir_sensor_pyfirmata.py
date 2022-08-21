from pyfirmata import Arduino, util
import time

board = Arduino("/dev/ttyACM0")

it = util.Iterator(board)
it.start()

ir_sensor = board.analog[0]
ir_sensor.enable_reporting()
while True:
    val = ir_sensor.read()
    # find centimeter conversion formula in johnny five: https://github.com/rwaldron/johnny-five/blob/main/lib/proximity.js#L62
    # arduino analog reads voltage as integers between 0 to 1023
    # pyfirmata linearly translates the range to 0 to 1, so *1023
    range_cm = 2076 / (val * 1023 - 11)
    print(range_cm)
    time.sleep(0.1)
