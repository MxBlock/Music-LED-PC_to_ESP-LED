import serial
import sounddevice as sd
import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

def serial_read():
    data = arduino.readline()
    return data

def serial_write(data):
    arduino.write((str(data) + '\n').encode('utf-8'))
    arduino.flush()

def list_audio_devices():
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        print(f"Device {i} - {device['name']}")

def get_current_volume(): #From loculu
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    return volume.GetMasterVolumeLevelScalar()

def capture_audio_data():
    global device_index
    global sampling_frames
    global sampling_frequency
    audio_data = sd.rec(frames=sampling_frames, samplerate=sampling_frequency, channels=1, dtype='int16', device=device_index)
    sd.wait()
    return audio_data

def define_brightness_by_volume(audio_data):
    global input_minVal
    global input_maxVal
    # Calculate volume as the average amplitude
    volume = np.abs(audio_data).mean()
    #Update min/max
    #input_minVal = min(input_minVal, volume)
    #input_maxVal = max(input_maxVal, volume)

    # Scale the volume to a value between 0 and 255
    #scaled_volume = int(np.interp(volume, [input_minVal, input_maxVal], [1, 255]))
    scaled_volume = int(np.interp(volume, [0, 32767], [0, 255]))
    return scaled_volume

def display_plot(data):
    plt.plot(data)
    plt.title("Audio")
    plt.xlabel("t")
    plt.ylabel("Δ")
    plt.show()

def display_real_time_plot(data):
    y = np.random.random()
    plt.scatter(i, y)
    plt.pause(0.05)


# Configure the serial connection
arduino = serial.Serial(port='COM6', baudrate=19200, timeout=.1)

device_index = 2

input_minVal = 32767
input_maxVal = 0

sampling_duration = 0.017   # Duration of audio capture in seconds
sampling_frequency = 44100  # Sampling frequency (must be at least twice as highest sampled frequency)
sampling_frames = int(sampling_duration * sampling_frequency)

#list_audi_devices()
while True:
    #sample = capture_audio_data()
    #display_plot(sample)
    #Y = np.abs(np.fft.fft(sample))
    #N = len(Y)/2+1
    #Z = Y[:N]
    data = capture_audio_data()
    #serial_write()
    display_plot(data)
    serial_write(define_brightness_by_volume(data))
    #time.sleep(1)