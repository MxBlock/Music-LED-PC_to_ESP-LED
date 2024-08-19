# to display in separate Tk window
import matplotlib
matplotlib.use('TkAgg')
import socket
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from scipy.fftpack import fft
from tkinter import TclError
import time


# ------------ Audio Setup ---------------
# constants
CHUNK = 1024*2	             # samples per frame
FORMAT = pyaudio.paInt16     # audio format (bytes per sample?)
CHANNELS = 1                 # single channel for microphone
RATE = 44100                 # samples per second
# Signal range is -32k to 32k
# limiting amplitude to +/- 4k
AMPLITUDE_LIMIT = 32767

# pyaudio class instance
p = pyaudio.PyAudio()

# stream object to get data from microphone
stream = p.open(
	format=FORMAT,
	channels=CHANNELS,
	rate=RATE,
	input=True,
	output=True,
    input_device_index=2,
	frames_per_buffer=CHUNK
)

# ------------ Plot Setup ---------------
fig, (ax1, ax2) = plt.subplots(2, figsize=(15, 7))
# variable for plotting
x = np.arange(0, 2 * CHUNK, 2)       # samples (waveform)
xf = np.linspace(0, RATE, CHUNK)     # frequencies (spectrum)

# create a line object with random data
line, = ax1.plot(x, np.random.rand(CHUNK), '-', lw=2)

# create semilogx line for spectrum, to plot the waveform as log not lin
line_fft, = ax2.semilogx(xf, np.random.rand(CHUNK), '-', lw=2)

# format waveform axes
ax1.set_title('AUDIO WAVEFORM')
ax1.set_xlabel('samples')
ax1.set_ylabel('volume')
ax1.set_ylim(-AMPLITUDE_LIMIT, AMPLITUDE_LIMIT)
ax1.set_xlim(0, 2 * CHUNK)
plt.setp(ax1, xticks=[0, CHUNK, 2 * CHUNK], yticks=[-AMPLITUDE_LIMIT, 0, AMPLITUDE_LIMIT])

# format spectrum axes
ax2.set_xlim(20, RATE / 2)

# Configure the serial connection
#arduino = serial.Serial(port='COM5', baudrate=19200, timeout=.1)

host = "192.168.168.193"
port = 80
#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP

def on_close(evt):	
	# Close the stream and terminate pyAudio
	stream.stop_stream()
	stream.close()
	p.terminate()
	sock.close()
	quit()

def fft_stuff(data_np):
	# compute FFT and update line
	yf = fft(data_np)
	magnitude = np.abs(yf[0:CHUNK])
	# The fft will return complex numbers, so np.abs will return their magnitude
	
	y=255
	x = np.argmax(magnitude)
	if magnitude[x] > 75:
		y = np.interp((x), [0, 1000], [0, 255])
	return y

def define_brightness_by_volume(audio_data):
    volume = np.abs(audio_data).max()
    scaled_volume = int(np.interp(volume, [0, AMPLITUDE_LIMIT], [0, 255]))
    return scaled_volume

def animate(i):
	"""
	# binary data
	data = stream.read(CHUNK)  
	# Open in numpy as a buffer
	data_np = np.frombuffer(data, dtype='h')
	# Update the line graph
	line.set_ydata(data_np)
	y = define_brightness_by_volume(data_np)
	#sock.sendall(bytes((str(y) + '\n').encode())) #TCP
	z = bytes(str(y), 'utf-8')
	print(z)
	sock.sendto(z, (host, port)) #UDP
	"""
	# binary data
	data = stream.read(CHUNK)
	# Open in numpy as a buffer
	data_np = np.frombuffer(data, dtype='h')
	# Update the line graph
	line.set_ydata(data_np)
	y = define_brightness_by_volume(data_np)
	z = y.to_bytes(1, byteorder='big')  # Assuming 'int' is 1 bytes
	#print("Sending:", y)
	sock.sendto(z, (host, port))  # UDP


sock.connect((host, port))
if __name__ == '__main__':
	anim = animation.FuncAnimation(fig, animate, blit=False, interval=100, cache_frame_data=False)
	fig.canvas.mpl_connect('close_event',  on_close)
	plt.show()