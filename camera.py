import io
import socket
import struct
import os
import time
import cv2
import cv2.cv as cv
import numpy as np
from pantilthat import *


class VideoCamera(object):
    def __init__(self):
        os.system('sudo modprobe bcm2835-v4l2')  # Use pi camera as usb device
        self.camera = cv.CreateCameraCapture(0)  # Set up camera
        # Load cascade data
        self.cascade = cv.Load(
            '/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml')

        self.cam_pan = 90  # Initial pan angle
        self.cam_tilt = 90  # Initial tilt angle

        pan(self.cam_pan - 90)  # Pan to initial position
        tilt(self.cam_tilt - 90)  # Tilt to initial position

        self.min_size = (15, 15)  # Minimum window size
        self.image_scale = 5  # Image shrink scale
        # The factor by which the search window is scaled between the
        # subsequent scans
        self.haar_scale = 1.2
        self.min_neighbors = 2  # Minimum number of neighbor rectangles that makes up an object
        self.haar_flags = cv.CV_HAAR_DO_CANNY_PRUNING  # Mode of operation

        if self.camera:
            self.frame_copy = None

        # Camera warm up
        time.sleep(2)

    def get_frame(self):
        try:
            frame = cv.QueryFrame(self.camera)
            if not frame:
                print('Camera error')
                return
            if not self.frame_copy:
                self.frame_copy = cv.CreateImage(
                    (frame.width, frame.height), cv.IPL_DEPTH_8U, frame.nChannels)
            if frame.origin == cv.IPL_ORIGIN_TL:
                cv.Flip(frame, frame, -1)

            # Our operations on the frame come here
            gray = cv.CreateImage((frame.width, frame.height), 8, 1)
            small_img = cv.CreateImage(
                (cv.Round(
                    frame.width /
                    self.image_scale),
                    cv.Round(
                    frame.height /
                    self.image_scale)),
                8,
                1)

            # convert color input image to grayscale
            cv.CvtColor(frame, gray, cv.CV_BGR2GRAY)

            # Scale input image for faster processing
            cv.Resize(gray, small_img, cv.CV_INTER_LINEAR)

            cv.EqualizeHist(small_img, small_img)

            midFace = None

            if(self.cascade):
                t = cv.GetTickCount()
                # Do haar detection
                faces = cv.HaarDetectObjects(
                    small_img,
                    self.cascade,
                    cv.CreateMemStorage(0),
                    self.haar_scale,
                    self.min_neighbors,
                    self.haar_flags,
                    self.min_size)
                t = cv.GetTickCount() - t
                if faces:
                    if not os.path.isfile('face.jpg'):
                        # Save temporary image if no existing one
                        image = cv2.imencode(
                            '.jpeg', np.asarray(frame[:, :]))[1]
                        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
                        cv2.imwrite('face.jpg', image)

                    for ((x, y, w, h), n) in faces:
                        # Resize the input, scale the bounding box of each face and convert to two
                        # CvPoints
                        pt1 = (int(x * self.image_scale),
                               int(y * self.image_scale))
                        pt2 = (int((x + w) * self.image_scale),
                               int((y + h) * self.image_scale))
                        cv.Rectangle(
                            frame, pt1, pt2, cv.RGB(
                                100, 220, 255), 1, 8, 0)
                        # Calculate mid point of the face
                        x1, y1 = pt1
                        x2, y2 = pt2

                        midFaceX = x1 + ((x2 - x1) / 2)
                        midFaceY = y1 + ((y2 - y1) / 2)
                        midFace = (midFaceX, midFaceY)

                        # Calculate offset of camera angle
                        offsetX = midFaceX / float(frame.width / 2)
                        offsetY = midFaceY / float(frame.height / 2)
                        offsetX -= 1
                        offsetY -= 1

                        self.cam_pan -= (offsetX * 5)
                        self.cam_tilt += (offsetY * 5)
                        self.cam_pan = max(0, min(180, self.cam_pan))
                        self.cam_tilt = max(0, min(180, self.cam_tilt))

                        # Use for debug
                        '''
                        print(
                            offsetX,
                            offsetY,
                            midFace,
                            self.cam_pan,
                            self.cam_tilt,
                            frame.width,
                            frame.height)
                        '''

                        # Pan and tilt to the nex position
                        pan(int(self.cam_pan - 90))
                        tilt(int(self.cam_tilt - 90))
                        
            # Push processed framge image to flask
            image = cv2.imencode('.jpeg', np.asarray(frame[:, :]))[
                1].tostring()
            return image
        except Exception as e:
            print(e)
            return
