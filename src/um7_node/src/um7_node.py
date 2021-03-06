#!/usr/bin/env python3

"""
Created on Wed Oct 14 16:26:49 2020
Webpage IMU: https://pypi.org/project/um7py/
@author: Sebastian Tilaguy
"""

import rospy
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Quaternion, Vector3
#from tf.transformations import quaternion_from_euler
import numpy as np

from um7py import UM7Serial

def deg2rad(angle):
    out = angle*np.pi/180.0
    return out

def quaternion_from_euler(roll, pitch, yaw):
    cy = np.cos(yaw * 0.5)
    sy = np.sin(yaw * 0.5)
    cp = np.cos(pitch * 0.5)
    sp = np.sin(pitch * 0.5)
    cr = np.cos(roll * 0.5)
    sr = np.sin(roll * 0.5)

    q = Quaternion()
    # print(q)
    q.w = cr * cp * cy + sr * sp * sy
    q.x = sr * cp * cy - cr * sp * sy
    q.y = cr * sp * cy + sr * cp * sy
    q.z = cr * cp * sy - sr * sp * cy

    return q
    
class IMU_node():
    def __init__(self):
        # Quaternion data
        self.q = 0.0
        # angular velocities data
        self.velocities = 0.0
        #initial param
        port = rospy.get_param('/um7_node/device_port')
        
        rospy.init_node('UM7_node')
        
        self.um7_serial = UM7Serial(port_name=port)
        self.um7_serial.zero_gyros = 1
        
        self.run()
    
    def run(self):
        pub = rospy.Publisher('/um7', Imu, queue_size=10)
        rate = rospy.Rate(100) # 100hz
        while not rospy.is_shutdown():
            self.UM7(self.um7_serial)
            
            mesg = Imu()
            mesg.header.stamp = rospy.Time.now()
            mesg.header.frame_id = 'UM7'
            mesg.orientation = self.q
            mesg.angular_velocity = Vector3(*self.velocities)
            
            pub.publish(mesg)
            rate.sleep()
    
    
    def UM7(self,IMU):
        for packet in IMU.recv_euler_broadcast(1):
            # print(f"packet: {packet}")
            roll = packet.roll
            pitch = packet.pitch
            yaw = packet.yaw
            self.velocities = [packet.roll_rate, packet.pitch_rate, packet.yaw_rate]
            self.q = quaternion_from_euler(deg2rad(roll), deg2rad(pitch), deg2rad(yaw))

if __name__ == '__main__':
    try:
        IMU_node()
    except rospy.ROSInterruptException:
        pass
