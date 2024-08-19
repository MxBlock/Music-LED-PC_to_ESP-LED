 
import socket
import time

# Configure the serial connection
host = "192.168.168.193"
port = 80
#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP

def on_close(evt):    
    # Close the stream and terminate pyAudio
    sock.close()
    quit()

def send_int(x):
    z = x.to_bytes(1, byteorder='big')  # Assuming 'int' is 1 byte
    sock.sendto(z, (host, port))

def send_intArr(arr):
    # Convert the integer array to a comma-separated string
    data = ','.join(map(str, arr))
    # Encode the string to bytes
    z = data.encode('utf-8')
    #print(z)
    sock.sendto(z, (host, port))

sock.connect((host, port))
if __name__ == '__main__':
    while True:
        send_intArr((255,0,0))
        print("r")
        time.sleep(1)
        send_intArr((0,255,0))
        print("g")
        time.sleep(1)
        send_intArr((0,0,255))
        print("b")
        time.sleep(1)