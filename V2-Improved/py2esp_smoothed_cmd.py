import socket, pyaudio, numpy as np
from collections import deque

# Config parameters
CHUNK = 560
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
DECAY_FACTOR = 0.98
INIT_MAX = 5000
SMOOTH_WIN = 5
DECAY_RATE = 0.85
HOST, PORT = "192.168.42.240", 80

# Setup audio and UDP
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                input=True, frames_per_buffer=CHUNK, input_device_index=3)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect((HOST, PORT))

max_amp = INIT_MAX
history = deque(maxlen=SMOOTH_WIN)

while True:
    data = stream.read(CHUNK)
    audio = np.frombuffer(data, dtype='h')
    vol = np.abs(audio).max()
    max_amp = vol if vol > max_amp else max_amp * DECAY_FACTOR
    norm = vol / max_amp
    history.append(norm)
    weights = np.exp(np.linspace(0, DECAY_RATE, len(history)))
    weights /= weights.sum()
    smoothed = np.dot(history, weights) if len(history) > 1 else norm
    brightness = int(smoothed**2 * 255)
    sock.send((','.join([str(brightness)] * 3)).encode())
