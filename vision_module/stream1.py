import cv2
import socket
import struct
import numpy as np

# Create a socket for receiving data
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_ip = '192.168.1.1'
port = 5000  # Must be the same as in the sender

socket_address = (host_ip, port)

# Bind to the address and listen
server_socket.bind(socket_address)
server_socket.listen(5)
print("Listening at:", socket_address)
