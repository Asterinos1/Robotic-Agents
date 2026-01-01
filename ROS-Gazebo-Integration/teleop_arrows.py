import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys, select, termios, tty

msg = """
Control Your Robot!
---------------------------
Moving around:
   ↑ : Forward
   ↓ : Backward
   ← : Left (Turn)
   → : Right (Turn)

Space/S : Stop
CTRL-C to quit
"""

moveBindings = {
    '\x1b[A': (1, 0),  # Up
    '\x1b[B': (-1, 0), # Down
    '\x1b[C': (0, -1), # Right
    '\x1b[D': (0, 1),  # Left
}

def get_key(settings):
    tty.setraw(sys.stdin.fileno())
    select.select([sys.stdin], [], [], 0.1)
    key = sys.stdin.read(1)
    if key == '\x1b': # Handle multi-byte arrow keys
        key += sys.stdin.read(2)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def main():
    settings = termios.tcgetattr(sys.stdin)
    rclpy.init()
    node = rclpy.create_node('teleop_arrows')
    pub = node.create_publisher(Twist, 'cmd_vel', 10)

    speed = 0.5 # m/s
    turn = 1.0  # rad/s

    try:
        print(msg)
        while True:
            key = get_key(settings)
            x = 0.0
            th = 0.0
            
            if key in moveBindings.keys():
                x = moveBindings[key][0]
                th = moveBindings[key][1]
            elif key.lower() == ' ' or key.lower() == 's':
                x = 0.0
                th = 0.0
            elif key == '\x03': # CTRL-C
                break

            twist = Twist()
            twist.linear.x = x * speed
            twist.angular.z = th * turn
            pub.publish(twist)

    except Exception as e:
        print(e)
    finally:
        twist = Twist()
        pub.publish(twist)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

if __name__ == '__main__':
    main()
