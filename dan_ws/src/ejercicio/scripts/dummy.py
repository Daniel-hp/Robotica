#!/usr/bin/env python
# license removed for brevity

## Se sigue de  : https://www.clearpathrobotics.com/2014/09/ros-101-creating-node/ ##
## http://wiki.ros.org/tf/Tutorials/Writing%20a%20tf%20listener%20%28Python%29
import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Twist


def talker():
    pub = rospy.Publisher('chatter', Twist, queue_size=100)
    rospy.init_node('talker', anonymous=True)
    rate = rospy.Rate(10) # 10hz
    while not rospy.is_shutdown():
        hello_str = "hello world %s" % rospy.get_time()
        linear = 2
        angular = 4
        cmd = Twist()
        cmd.linear.x = linear
        cmd.angular.z = angular
        rospy.loginfo("WII")
        pub.publish(cmd)
        rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass