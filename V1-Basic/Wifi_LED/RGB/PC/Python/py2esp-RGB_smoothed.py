 
import socket
import pyaudio
import numpy as np
from scipy.fftpack import fft
from tkinter import TclError
import time


# ------------ Audio Setup ---------------
# constants
CHUNK = 560                     # samples per frame - base value 1024*2 (22Hz) - 736 (60Hz) - min: 128 (340Hz) - recomended: 380 (120Hz)
FORMAT = pyaudio.paInt16     # audio format (bytes per sample?)
CHANNELS = 1                 # single channel for microphone
RATE = 44100                 # samples per second #44100
# Signal range is -32k to 32k
# limiting amplitude to +/- 4k
AMPLITUDE_LIMIT = 26000 #32767
#FREQ_RANGE = 800  # Hz
#N = int(RATE / FREQ_RANGE) #Need to be double the FREQ_RANGE for losses in the fft calculations (only use positive-frequency)

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

# Configure the serial connection
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

def define_brightness_by_fft(audio_data):
    volume = np.abs(audio_data).max()
    #scaled_volume = np.interp(volume, [0, AMPLITUDE_LIMIT], [0, 1.0])
    output = 0
    if volume >= 10:
        windowed_data = audio_data * np.blackman(len(audio_data))
        # compute FFT and update line
        fftArr = fft(windowed_data)
        # The fft will return complex numbers, so np.abs will return their magnitude
        frequencyMagnitudeArr = np.abs(fftArr[1:int(CHUNK/2)])
        maxFreq = np.argmax(frequencyMagnitudeArr)
        # Normalize the magnitude to a range of 0 to 255
        #interpedMagnitude = np.interp(1/(maxFreq+1), [0, CHUNK], [255.0, 0])
        output = int(np.interp(volume*(0.5**maxFreq), [0, AMPLITUDE_LIMIT], [0, 255.0]))
        #print(volume, maxFreq, output)
    return output

def define_brightness_by_volume(audio_data):
    volume = np.abs(audio_data).max()
    scaled_volume = int(np.interp(volume, [0, AMPLITUDE_LIMIT], [0, 255]))
    return scaled_volume

def animate():
    global prev_output
    global zero_counter
    # binary data
    data = stream.read(CHUNK)
    # Open in numpy as a buffer
    data_np = np.frombuffer(data, dtype='h')
    y = define_brightness_by_fft(data_np)
    #y = define_brightness_by_volume(data_np)
    
    smoothed_r = low_pass_filter(prev_output[0], y, 0.2)
    smoothed_g = low_pass_filter(prev_output[1], y, 0.2)
    smoothed_b = low_pass_filter(prev_output[2], y, 0.2)
    prev_output[0] = smoothed_r
    prev_output[1] = smoothed_g
    prev_output[2] = smoothed_b

    #RGB = [smoothed_r,int(smoothed_g*0.2),smoothed_b] # lila
    #RGB = [0,smoothed_g,int(smoothed_b*0.83)] # kaiju
    RGB = [smoothed_r,smoothed_g,smoothed_b] # white
    #RGB = [0,smoothed_g,smoothed_b] # türkis
    #RGB = [smoothed_r,0,0] # red
    #RGB = [0,smoothed_g,0] # green
    #RGB = [0,0,smoothed_b] # blue
    #print(RGB)
    #ColorCycle(1)
    
    
    send_intArr(RGB)

def low_pass_filter(prev_output, current_value, alpha):
    if prev_output is None:
        prev_output = current_value
    else:
        prev_output = alpha * current_value + (1 - alpha) * prev_output
    return int(prev_output)

def ColorCycle(s):
    global prev_output_RGB
    
    for i in range(3):
        if abs(prev_output_RGB[i]) >= 255 or prev_output_RGB[i] == 0:
            prev_output_RGB[i] *= -1
        prev_output_RGB[i] += s

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

alpha = 0.15 # Higer = more responsive - good value: 0.2
prev_output = [None,None,None]
zero_counter = 10
prev_output_RGB = [0,0,0]



sock.connect((host, port))
if __name__ == '__main__':
    while True:
        animate()