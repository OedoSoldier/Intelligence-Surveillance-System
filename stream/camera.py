import io
import socket
import struct
import cv2
import numpy as np

class VideoCamera(object):
    def __init__(self):
        # Start a socket listening for connections on 0.0.0.0:8000 (0.0.0.0 means
        # all interfaces)
        self.client_socket = socket.socket()
        self.client_socket.connect(('10.0.0.214', 8000))
        # Accept a single connection and make a file-like object out of it
        self.connection = self.client_socket.makefile('rb')
    
    def __del__(self):
        self.connection.close()
        self.client_socket.close()
    
    def get_frame(self):
        image_len = struct.unpack('<L', self.connection.read(struct.calcsize('<L')))[0]
        # Construct a stream to hold the image data and read the image
        # data from the connection
        image_stream = io.BytesIO()
        image_stream.write(self.connection.read(image_len))
        # Rewind the stream, open it as an image with PIL and do some
        # processing on it
        image_stream.seek(0)
        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        return image_stream.getvalue()