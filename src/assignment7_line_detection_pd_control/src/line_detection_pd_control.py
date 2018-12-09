'''
The Algorithm:
* Launch the lane_detection node and get the line equation with Ransac (assignment 6). 
* New feature added: custom message type Line for detected slope and intercept
* Launch the simple_drive_control node 
* Calculate an error using PD controller from line parameters (new code created for assignment 7)
* Create a command for an actuator (code from assignment 6)
* Move a mobile robot
* Detect the new line position and calculate a new error and a new command and perform the next movement
'''

#imports from previous assignments
import line as ln
import steer_calibration as st

#python imports
import sys
import cv2
from matplotlib import pyplot as plt
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import numpy as np
from sklearn import linear_model
from assignment7_line_detection_pd_control.msg import Line

class pd_controller:
    def __init__(self):
        self.pd_controller_sub = rospy.Subscriber("/line_parameters", Line, self.callback, queue_size=1)
        self.pd_error = None
        self.derivative = None
        self.control_variable = None
        self.kp = 0.5
        self.kd = 1.2
        
    def callback(self, data):
        slope = data.slope
        intercept = data.intercept
        
        camera_height = data.height
        camera_width = data.width
        
        # we want two lines to intersect in the middle_of_the_screen = camera_width / 2
        target_position = camera_width / 2
        
        # Get the current position
        # solving the equations:
        # y1 = h / 2 (horizontal line in the middle of camera)
        # y2 = slope * x + intercept
        # y1 = y2 = (camera_height / 2 - intercept) / k
        current_position = (camera_height / 2 - intercept) / slope
        
        last_pd_error = self.pd_error
        
        #Calculate the error (P Controller)
        self.pd_error = target_position - current_position

        '''
        Calculation error change (D part)
        Negative values of derivative indicate an improvement (reduction) in the error signal. 
        For example, if the last error was 20 and the current error is 10, the derivative will be -10. 
        When these negative values are multiplied with a constant, Kd, and are added to the output of the loop, 
        it can slow down the system when approaching the target.
        '''
        self.derivative = self.pd_error - last_pd_error

        #Calculate the control variable
        control_variable = self.kp * self.pd_error + self.kd * self.derivative
        
        # move a car
        


def main(args):
    rospy.init_node('pd_controller', anonymous=True)
    commands = st.calibrate_steer()
    pd_controller = pd_controller()
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down")
    cv2.destroyAllWindows()    
    
if __name__ == '__main__':
    main(sys.argv)


