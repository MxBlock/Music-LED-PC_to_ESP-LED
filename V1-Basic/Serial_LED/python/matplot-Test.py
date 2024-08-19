import csv
import numpy as np
import matplotlib.pyplot as plt

x = 0


#plt.xlabel('Time ($s$)')
#plt.ylabel('Amplitude ($Unit$)')
while True:
    t = np.linspace(x, 2*np.pi, 1000, endpoint=True)
    f = 3.0 # Frequency in Hz
    A = 100.0 # Amplitude in Unit
    s = A * np.sin(2*np.pi*f*t) # Signal
    plt.plot(t,s)
    plt.show()
    x = x+0.1

