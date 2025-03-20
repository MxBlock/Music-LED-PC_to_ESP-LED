import socket, pyaudio, numpy as np, threading
from collections import deque

# Configuration
CHUNK = 560
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
DECAY = 0.98
INIT_MAX = 5000
SMOOTH = 5
DECAY_RATE = 0.85
HOST, PORT = "192.168.42.240", 80

# Initialize variables
max_amp = max(INIT_MAX, 1)
history = deque(maxlen=SMOOTH)
color = {'r': 255, 'g': 255, 'b': 255}

# Setup audio and UDP
p = pyaudio.PyAudio()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK, input_device_index=3)
sock.connect((HOST, PORT))

def print_help():
    print(f"Commands:\n  r/g/b [0-255] - Set color intensity (Current: {color})\n  rgb R G B - Set all colors at once (e.g., rgb 255 0 100)\n  dr [0.01-1.0] - Set decay rate (Current: {DECAY_RATE})\n  sw [1-50] - Set smoothing window (Current: {SMOOTH})\n  df [0.8-1.0] - Set decay factor (Current: {DECAY})")

def listen():
    global DECAY_RATE, SMOOTH, DECAY, history
    while True:
        try:
            cmd = input().strip().split()
            if len(cmd) == 4 and cmd[0] == 'rgb':
                try:
                    r, g, b = map(int, cmd[1:])
                    color['r'], color['g'], color['b'] = max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))
                    print(f"Updated color: {color}")
                except ValueError:
                    print("Invalid RGB format. Use: rgb 255 0 100")
                    print_help()
            elif len(cmd) == 2:
                key, value = cmd[0], cmd[1]
                value = float(value) if '.' in value else int(value)
                match key:
                    case 'r' | 'g' | 'b':
                        color[key] = max(0, min(255, int(value)))
                        print(f"Updated color: {color}")
                    case 'dr':
                        DECAY_RATE = max(0.01, min(1.0, value))
                    case 'sw':
                        SMOOTH = max(1, min(50, int(value)))
                        history = deque(maxlen=SMOOTH)
                    case 'df':
                        DECAY = max(0.8, min(1.0, value))
                    case _:
                        print("Invalid command.")
                        print_help()
            elif len(cmd) == 1 and cmd[0] == 'help':
                print_help()
            else:
                print("Invalid command.")
                print_help()
        except:
            print("Invalid input.")
            print_help()

threading.Thread(target=listen, daemon=True).start()

while True:
    vol = np.abs(np.frombuffer(stream.read(CHUNK), dtype='h')).max()
    max_amp = max(vol if vol > max_amp else max_amp * DECAY, 1)
    norm = vol / max_amp
    history.append(norm)
    weights = np.exp(np.linspace(0, DECAY_RATE, len(history)))
    weights /= weights.sum()
    smoothed = np.dot(history, weights) if len(history) > 1 else norm
    brightness = int(smoothed**2 * 255)
    sock.send(f"{int(color['r'] * (brightness / 255))},{int(color['g'] * (brightness / 255))},{int(color['b'] * (brightness / 255))}".encode())