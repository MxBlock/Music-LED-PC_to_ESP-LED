import socket

host = "192.168.168.193"  # Replace with the IP address assigned to your ESP8266
port = 80

# Create a socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.connect((host, port))
    message = "Hello ESP8266!"
    s.sendall(message.encode())
finally:
    s.close()
