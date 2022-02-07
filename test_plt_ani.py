"""
Sources for help:

stackoverflow example
https://stackoverflow.com/questions/52858696/matplotlib-not-responding-after-a-interactive-plotting

plt example
https://matplotlib.org/stable/gallery/animation/animate_decay.html

plt docs on FuncAnimation
https://matplotlib.org/stable/api/_as_gen/matplotlib.animation.FuncAnimation.html



"""


import time
import serial
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import itertools

def data_gen():
  for cnt in itertools.count():
    t = cnt / 10
    yield t, np.sin(2*np.pi*t) * np.exp(-t/10.)

fig, ax = plt.subplots()
line,= ax.plot([],[])
ax.set_ylabel("Nozzle Temp")
ax.set_xlabel('Time')

nozzle_temp_data = np.array([])
time_data = np.array([])

timestep = 500 #ms

def run(data):
  global nozzle_temp_data, time_data
  t, y = data
  nozzle_temp_data = np.append(nozzle_temp_data, y)
  time_data = np.append(time_data, t)
  line.set_data(time_data, nozzle_temp_data)
  ax.autoscale()
  ax.relim()
  ax.autoscale_view()

ani = animation.FuncAnimation(fig, run, data_gen, interval=timestep)

def save_fig(event):
  if event.key == 's':
    ani.event_source.stop()
    # fig.savefig('test.png')
    plt.savefig("./test_2.pdf")
    print("Saved Figure")

cid = fig.canvas.mpl_connect('key_press_event', save_fig)

plt.show()

