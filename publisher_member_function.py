import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Range

from pyfirmata import Arduino, util

board = Arduino("/dev/ttyACM0")

it = util.Iterator(board)
it.start()

ir_sensor = board.analog[0]
ir_sensor.enable_reporting()


def get_range(ir_sensor):
    val = ir_sensor.read()
    # find centimeter conversion formula in johnny five: https://github.com/rwaldron/johnny-five/blob/main/lib/proximity.js#L62
    # arduino analog reads voltage as integers between 0 to 1023
    # pyfirmata linearly translates the range to 0 to 1, so *1023
    range_cm = 2076 / (val * 1023 - 11)
    return range_cm


class MinimalPublisher(Node):
    def __init__(self):
        super().__init__("minimal_publisher")
        self.publisher_ = self.create_publisher(Range, "topic", 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = Range()
        # use message parameters from: http://wiki.ros.org/rosserial_arduino/Tutorials/IR%20Ranger
        # For GP2Y0A41SK0F only. Adjust for other IR rangers
        msg.radiation_type = 1
        msg.field_of_view = 0.01
        msg.min_range = 0.04
        msg.max_range = 0.3
        range_cm = get_range(ir_sensor)
        msg.range = range_cm / 100  # in meters

        self.publisher_.publish(msg)
        self.get_logger().info(f"Hand is {round(msg.range,3)}m away")
        self.i += 1


def main(args=None):
    rclpy.init(args=args)

    minimal_publisher = MinimalPublisher()

    rclpy.spin(minimal_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
