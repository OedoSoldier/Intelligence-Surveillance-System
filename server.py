import io
import socket
import struct
import os
import cv2
import time
import cv2.cv as cv
import numpy as np
from pantilthat import *

print('Initializing...')

os.system('sudo modprobe bcm2835-v4l2')
camera = cv.CreateCameraCapture(0)
cascade = cv.Load(
    '/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml')

cam_pan = 90
cam_tilt = 90

pan(cam_pan - 90)
tilt(cam_tilt - 90)

'''
light_mode(WS2812)
def lights(r,g,b,w):
    for x in range(18):
        set_pixel_rgbw(x,r if x in [3,4] else 0,g if x in [3,4] else 0,b,w if x in [0,1,6,7] else 0)
    show()
lights(0,0,0,50)
'''

min_size = (15, 15)
image_scale = 5
haar_scale = 1.2
min_neighbors = 2
haar_flags = cv.CV_HAAR_DO_CANNY_PRUNING

if camera:
    frame_copy = None

print('Waiting connection...')

# Start a socket listening for connections on 0.0.0.0:8000 (0.0.0.0 means
# all interfaces)
server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(1)

while True:
    # Make a file-like object out of the connection
    (connection, (ip, port)) = server_socket.accept()
    print('Connnection from {}:{} detected!'.format(ip, port))
    try:
        # Start a preview and let the camera warm up for 2 seconds
        time.sleep(2)

        # Note the start time and construct a stream to hold image data
        # temporarily (we could write it directly to connection but in this
        # case we want to find out the size of each capture first to keep
        # our protocol simple)
        while True:
            frame = cv.QueryFrame(camera)
            if not frame:
                cv.WaitKey(0)
                break
            if not frame_copy:
                frame_copy = cv.CreateImage((frame.width, frame.height),
                                            cv.IPL_DEPTH_8U, frame.nChannels)
            if frame.origin == cv.IPL_ORIGIN_TL:
                cv.Flip(frame, frame, -1)

            # Our operations on the frame come here
            gray = cv.CreateImage((frame.width, frame.height), 8, 1)
            small_img = cv.CreateImage(
                (cv.Round(
                    frame.width /
                    image_scale),
                    cv.Round(
                    frame.height /
                    image_scale)),
                8,
                1)

            # convert color input image to grayscale
            cv.CvtColor(frame, gray, cv.CV_BGR2GRAY)

            # scale input image for faster processing
            cv.Resize(gray, small_img, cv.CV_INTER_LINEAR)

            cv.EqualizeHist(small_img, small_img)

            midFace = None

            if(cascade):
                t = cv.GetTickCount()
                # HaarDetectObjects takes 0.02s
                faces = cv.HaarDetectObjects(
                    small_img,
                    cascade,
                    cv.CreateMemStorage(0),
                    haar_scale,
                    min_neighbors,
                    haar_flags,
                    min_size)
                t = cv.GetTickCount() - t
                if faces:
                    # lights(50 if len(faces) == 0 else 0, 50 if len(faces) > 0 else 0,0,50)

                    for ((x, y, w, h), n) in faces:
                        # the input to cv.HaarDetectObjects was resized, so scale the
                        # bounding box of each face and convert it to two
                        # CvPoints
                        pt1 = (int(x * image_scale), int(y * image_scale))
                        pt2 = (int((x + w) * image_scale),
                               int((y + h) * image_scale))
                        cv.Rectangle(
                            frame, pt1, pt2, cv.RGB(
                                100, 220, 255), 1, 8, 0)
                        # get the xy corner co-ords, calc the midFace location
                        x1 = pt1[0]
                        x2 = pt2[0]
                        y1 = pt1[1]
                        y2 = pt2[1]

                        midFaceX = x1 + ((x2 - x1) / 2)
                        midFaceY = y1 + ((y2 - y1) / 2)
                        midFace = (midFaceX, midFaceY)

                        offsetX = midFaceX / float(frame.width / 2)
                        offsetY = midFaceY / float(frame.height / 2)
                        offsetX -= 1
                        offsetY -= 1

                        cam_pan -= (offsetX * 5)
                        cam_tilt += (offsetY * 5)
                        cam_pan = max(0, min(180, cam_pan))
                        cam_tilt = max(0, min(180, cam_tilt))

                        print(
                            offsetX,
                            offsetY,
                            midFace,
                            cam_pan,
                            cam_tilt,
                            frame.width,
                            frame.height)

                        pan(int(cam_pan - 90))
                        tilt(int(cam_tilt - 90))
                        break

            image = cv2.imencode('.jpeg', np.asarray(frame[:, :]))[
                1].tostring()
            stream = io.BytesIO(image)
            # Write the length of the capture to the stream and flush to
            # ensure it actually gets sent
            connection.sendall(struct.pack('<L', len(image)))
            # Send the image data over the wire
            connection.sendall(stream.read())
            # Reset the stream for the next capture
            stream.seek(0)
            stream.truncate()
        # Write a length of zero to the stream to signal we're done
        # connection.sendall(struct.pack('<L', 0))
    except Exception as e:
        print(e)
    finally:
        connection.close()
        print('Waiting connection...')

server_socket.close()
