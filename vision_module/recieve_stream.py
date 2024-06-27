import cv2
import numpy as np
import socket

# IP address and port for receiving the stream
ip_address = '192.168.2.1'
port = 5000

# Initialize socket for receiving UDP stream
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ip_address, port))

# Define the frame size (must match the size sent from the Raspberry Pi)
frame_width = 640
frame_height = 480
frame_size = frame_width * frame_height * 3

# Buffer to hold incoming frame chunks
frame_buffer = bytearray()

while True:
    # Receive data from the socket
    data, _ = sock.recvfrom(65507)  # 65507 is the maximum size for a UDP packet data payload

    # Append received data to the frame buffer
    frame_buffer.extend(data)

    # If the frame buffer contains enough data for one frame, process it
    while len(frame_buffer) >= frame_size:
        # Extract the frame data
        frame_data = frame_buffer[:frame_size]
        frame_buffer = frame_buffer[frame_size:]

        # Convert frame data to numpy array
        frame = np.frombuffer(frame_data, dtype=np.uint8).reshape((frame_height, frame_width, 3))

        # Display the frame using OpenCV
        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Close the socket and OpenCV window
sock.close()
cv2.destroyAllWindows()


