#!/usr/bin/env python3
import rospy
from std_msgs.msg import String

def callback(msg):
    rospy.loginfo("I heard: %s", msg.data)

rospy.init_node('listener_node')
sub = rospy.Subscriber('chatter', String, callback)
rospy.spin()
