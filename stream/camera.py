import io
import socket
import struct
import cv2
import numpy as np

class VideoCamera(object):
    def __init__(self, server_socket):
        # Start a socket listening for connections on 0.0.0.0:8000 (0.0.0.0 means
        # all interfaces)
        # Accept a single connection and make a file-like object out of it
        self.connection = server_socket.accept()[0].makefile('rb')
    
    def __del__(self):
        self.connection.close()
    
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