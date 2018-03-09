import io
import socket
import struct
import cv2
import numpy as np

# Connect a client socket to my_server:8000 (change my_server to the
# hostname of your server)
client_socket = socket.socket()
client_socket.connect(('10.0.0.214', 8000))

# Accept a single connection and make a file-like object out of it
connection = client_socket.makefile('rb')
try:
    while True:
        # Read the length of the image as a 32-bit unsigned int. If the
        # length is zero, quit the loop
        image_len = struct.unpack(
            '<L', connection.read(
                struct.calcsize('<L')))[0]
        print(image_len)
        if not image_len:
            break
        # Construct a stream to hold the image data and read the image
        # data from the connection
        image_stream = io.BytesIO()
        image_stream.write(connection.read(image_len))
        # Rewind the stream, open it as an image with PIL and do some
        # processing on it
        image_stream.seek(0)
        image = np.fromstring(image_stream.getvalue(), dtype=np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        cv2.imshow('test', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
except Exception as e:
    print(e)
finally:
    connection.close()
    client_socket.close()
    cv2.destroyAllWindows()
