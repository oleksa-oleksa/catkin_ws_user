#!/usr/bin/env python
import rospy
from std_msgs.msg import String, Float32
import line as ld
import sys
import cv2
from matplotlib import pyplot as plt
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import numpy as np
from sklearn import linear_model


class lane_detection:
    def __init__(self):
        self.lane_detection_pub = rospy.Publisher("/image_processing/bin_img",Image, queue_size=1)
        
        self.bridge = CvBridge()
        self.lane_detection_sub = rospy.Subscriber("image_raw_subscriber", Float32, callback)
 
    def callback(self, data):
        try:
            img = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            print(e)
            
        # Crop 20% of the image along the y axis
        y_end = np.shape(img)[0]
        y_start = (np.shape(img)[0] * 0.2)
        img = img[int(y_start): int(y_end), :]
    
        # Convert RGB to HSV
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
        # define range of color in HSV
        lower = np.array([0, 40, 150])
        upper = np.array([18, 80, 255])
    
        # Threshold the HSV image to get only the lines colors
        mask = cv2.inRange(hsv, lower, upper)
    
        # Bitwise-AND mask and original image
        res = cv2.bitwise_and(img, img, mask=mask)
    
        seg1, seg2 = ld.line_segments(mask)
    
        m1, b1 = ld.ransac_method(seg1)
        print("Equation line 1: y1 = %fx + %f" % (m1, b1))
        m2, b2 = ld.ransac_method(seg2)
        print("Equation line 2: y2 = %fx + %f" % (m2, b2))
    
        line1 = ld.end_start_points(m1, b1, img.shape[1])
        line2 = ld.end_start_points(m2, b2, img.shape[1])
    
        ransac_lines = ld.show_lines(img, line1, line2)
        
        try:
            self.image_pub.publish(self.bridge.cv2_to_imgmsg(ransac_lines, "mono8"))
        except CvBridgeError as e:
            print(e)
    
def main(args):
    rospy.init_node('lane_detector', anonymous=True)
    lane_detector = lane_detection()
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down")
    cv2.destroyAllWindows()    
    

if __name__ == '__main__':
    main(sys.argv)
