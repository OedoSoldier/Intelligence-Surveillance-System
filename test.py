import requests
import json
import cv2
import io
import socket
import os
import time
import cv2.cv as cv
import numpy as np

print('Initializing...')

os.system('sudo modprobe bcm2835-v4l2')
camera = cv.CreateCameraCapture(0)

if camera:
    frame_copy = None

addr = 'http://10.0.0.130:5000'
test_url = addr + '/upload'

# prepare headers for http request
content_type = 'image/jpeg'
headers = {'content-type': content_type}

while True:
    frame = cv.QueryFrame(camera)
    if not frame:
        print('Camera error')
        break
    if not frame_copy:
        frame_copy = cv.CreateImage((frame.width, frame.height),
                                    cv.IPL_DEPTH_8U, frame.nChannels)
    if frame.origin == cv.IPL_ORIGIN_TL:
        cv.Flip(frame, frame, -1)
    # img = cv2.imread('lena.jpg')
    # encode image as jpeg
    #_, img_encoded = cv2.imencode('.jpg', img)
    image = cv2.imencode('.jpeg', np.asarray(frame[:, :]))[1].tostring()
    # send http request with image and receive response
    response = requests.post(test_url, data=image, headers=headers) # requests.post(test_url, data=image, headers=headers) 
    # decode response
    # print json.loads(response.text)
    print(response.text)
    # expected output: {u'message': u'image received. size=124x124'}
