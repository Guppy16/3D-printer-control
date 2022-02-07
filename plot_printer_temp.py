import time
from cv2 import repeat
import serial
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import utils

com = "COM6"
figname = f"./PID_tests/PID_tests_{time.time()}_"

timestep = 0.5 # seconds

ser = utils.get_serial_connection(port=com, baudrate=38400)

fig, ax = plt.subplots()
line,= ax.plot([],[])
ax.set_ylabel("Nozzle Temp")
ax.set_xlabel('Time')

nozzle_temp_data = np.array([])
time_data = np.array([])

def update(i):
  global nozzle_temp_data, time_data

  # If serial data not being read in time:
  # Read from serial here

  nozzle_temp_data = np.append(nozzle_temp_data, [utils.extract_nozzle_temp(ser)])
  time_data = np.append(time_data, [len(time_data) * timestep])
  line.set_data(time_data, nozzle_temp_data)
  ax.autoscale()
  ax.relim()
  ax.autoscale_view()

  # THEN Send command to printer
  ser.write(b'M105\r\n')

# Prematurely send command to printer
ser.write(b'M105\r\n')
ani = animation.FuncAnimation(fig, update, interval=timestep*100, frames=20, repeat=False)

def save_fig(event):
  if event.key == 's':
    ani.event_source.stop()
    # fig.savefig('test.png')
    plt.savefig(figname)
    print(f"Saved fig at: {figname}")
    utils.close_printer(ser)

cid = fig.canvas.mpl_connect('key_press_event', save_fig)

plt.show()

# Closing script
utils.close_printer(ser)

