#!/usr/bin/env python

from flask import Flask, render_template, Response
from camera import VideoCamera
import socket

application = Flask(__name__)

@application.route('/')
def index():
    return render_template('index.html')

def gen(camera):
    while True:
        try:
            frame = camera.get_frame()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        except Exception as e:
            pass # print(e)

@application.route('/video_feed')
def video_feed():
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', 8000))
    server_socket.listen(1)
    return Response(gen(VideoCamera(server_socket)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True)