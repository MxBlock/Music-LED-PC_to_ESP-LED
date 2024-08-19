import socket

# ESP8266 IP address and port
ESP_IP = '192.168.1.100'  # Replace with your ESP8266 IP address
ESP_PORT = 12345

def send_brightness(brightness)
    message = str(brightness).encode('utf-8')
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s
        s.sendto(message, (ESP_IP, ESP_PORT))

# Example usage send brightness value repeatedly
try
    while True
        brightness = float(input(Enter brightness (0.0 to 1.0) ))
        send_brightness(brightness)
except KeyboardInterrupt
    print(Program terminated.)
