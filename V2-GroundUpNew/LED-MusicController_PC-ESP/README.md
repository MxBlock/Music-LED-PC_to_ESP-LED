[Color]
r = 255
g = 0
b = 0

[Reciever]
host = 192.168.168.193
port = 80
;UDP or TCP
protocol = UDP

[Audio]
; samples per frame - base value 1024*2 (22Hz) - 736 (60Hz) - min: 128 (340Hz) - recomended: 380 (120Hz)
;560
WINDOW_SIZE = 560
;paFloat32 = 1 | paInt32 = 2 | paInt16 = 8
FORMAT = 8
CHANNELS = 1
RATE = 44100
INPUT_DEVICE_INDEX = 3
; Signal range is -32k to 32k
; limiting amplitude to +/- 4k
AMPLITUDE_LIMIT = 32767
;FREQ_RANGE = 800  # Hz
;N = int(RATE / FREQ_RANGE) #Need to be double the FREQ_RANGE for losses in the fft calculations (only use positive-frequency)

[Process]
;np.float32
npArrType = np.float32