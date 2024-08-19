
import math
import socket
import pyaudio
import numpy as np
from scipy.fftpack import fft
from tkinter import TclError
import numpy
import time


# ------------ Audio Setup ---------------
# constants
CHUNK = 560                     # samples per frame - base value 1024*2 (22Hz) - 736 (60Hz) - min: 128 (340Hz) - recomended: 380 (120Hz)
FORMAT = pyaudio.paInt16     # audio format (bytes per sample?)
CHANNELS = 1                 # single channel for microphone
RATE = 44100                 # samples per second #44100
# Signal range is -32k to 32k
# limiting amplitude to +/- 4k
AMPLITUDE_LIMIT = 32767
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

def plot_audio_and_detect_beats(audio_data):
    temp = numpy.empty(CHUNK, dtype=numpy.int16)
    temp = audio_data
    # get x and y values from FFT
    xs, ys = temp.fft
    
    # calculate average for all frequency ranges
    y_avg = numpy.mean(ys)

    # calculate low frequency average
    low_freq = [ys[i] for i in range(len(xs)) if xs[i] < 1000]
    low_freq_avg = numpy.mean(low_freq)
    
    global low_freq_avg_list
    low_freq_avg_list.append(low_freq_avg)
    cumulative_avg = numpy.mean(low_freq_avg_list)
    
    bass = low_freq[:int(len(low_freq)/2)]
    bass_avg = numpy.mean(bass)
    print("bass: {:.2f} vs cumulative: {:.2f}".format(bass_avg, cumulative_avg))
    
    # check if there is a beat
    # song is pretty uniform across all frequencies
    if (y_avg > 10 and (bass_avg > cumulative_avg * 1.5 or (low_freq_avg < y_avg * 1.2 and bass_avg > cumulative_avg))):
        global prev_beat
        curr_time = time.perf_counter()
        print(curr_time - prev_beat)
        if curr_time - prev_beat > 60/180: # 180 BPM max
            print("beat")
            # reset the timer
            prev_beat = curr_time
    
    # shorten the cumulative list to account for changes in dynamics
    if len(low_freq_avg_list) > 50:
        low_freq_avg_list = low_freq_avg_list[25:]
        print("REFRESH!!")

    # keep two 8-counts of BPMs so we can maybe catch tempo changes
    if len(bpm_list) > 24:
        bpm_list = bpm_list[8:]

    # reset song data if the song has stopped
    if y_avg < 10:
        bpm_list = []
        low_freq_avg_list = []
        print("new song")

def animate():
    global prev_output
    global zero_counter
    # binary data
    data = stream.read(CHUNK)
    # Open in numpy as a buffer
    data_np = np.frombuffer(data, dtype='h')
    y = define_brightness_by_fft(data_np)
    #y = define_brightness_by_volume(data_np)
    #y = plot_audio_and_detect_beats(data_np)
    
    smoothed_y = low_pass_filter(prev_output, y, alpha)
    prev_output = smoothed_y
    z = smoothed_y.to_bytes(1, byteorder='big')  # Assuming 'int' is 1 byte
    #z = y.to_bytes(1, byteorder='big')  # Assuming 'int' is 1 bytes
    #print("Sending:", y)
    sock.sendto(z, (host, port))  # UDP

def low_pass_filter(prev_output, current_value, alpha):
    if prev_output is None:
        prev_output = current_value
    else:
        prev_output = alpha * current_value + (1 - alpha) * prev_output
    return int(prev_output)

# Get the start time
#start_time = time.time()
#counter = 0
alpha = 0.2
prev_output = None
zero_counter = 10

sock.connect((host, port))
if __name__ == '__main__':
    while True:
        animate()
        """
        counter += 1

        # Calculate the elapsed time
        elapsed_time = time.time() - start_time
        # If one second has passed, print the frequency and reset the counter
        if elapsed_time >= 1:
            print("Frequency:", counter, "times per second")
            counter = 0
            start_time = time.time()  # Reset start time
        """