from asyncio import sleep
import time
from cv2 import repeat
import serial
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import utils


com = "COM6"
figname = f"./PID_tests/PID_tests_kp1_{time.time()}"

# Connect to printer
ser = utils.get_serial_connection(port=com, baudrate=38400)

# Define initial parameters
max_start_temp = 25
temp_target = 200
kp = 19.28
ki = 0.01
kd = 60

# Set PID control values
ser.write(f"M301 P{kp} I{ki} D{kd}\r\n".encode())
time.sleep(2)

timestep = 0.5 # seconds
max_timesteps = 30

# Setup figure
fig, ax = plt.subplots()
line,= ax.plot([],[], label="Nozzle Temperature")
target_line, = ax.plot([],[], label="Target Temperature")
ax.set_ylabel("Nozzle Temp")
ax.set_xlabel('Time')
ax.legend()

nozzle_temp_data = np.array([])
time_data = np.array([])
# target_data = np.array([])


def update(i):
  global nozzle_temp_data, time_data

  # Read temperature measurement
  # NOTE: This measurement lags behind by 0.5s (i.e. update interval)
  nozzle_temp_data = np.append(nozzle_temp_data, [utils.extract_nozzle_temp(ser)])
  time_data = np.append(time_data, [len(time_data) * timestep])
  
  # Replot line
  line.set_data(time_data, nozzle_temp_data)
  target_line.set_data(time_data, [temp_target for _ in time_data])
  ax.autoscale()
  ax.relim()
  ax.autoscale_view()

  # Send command to printer to measure temperature
  ser.write(b'M105\r\n')
    

# Heat up nozzle to desired temperature
# NOTE: MAY want to visualise this to check
# if temperature has truly settled
utils.set_nozzle_temp(ser, temp=temp_target, avg_num=10, tol=0.5)

# Set desired temperature
ser.write(f"M104 S{temp_target}\r\n".encode())

# Request temperature measurement
ser.write(b'M105\r\n')
ani = animation.FuncAnimation(fig, update, interval=int(timestep*1000), frames=int(max_timesteps/timestep), repeat=False)

def save_fig(event):
  if event.key == 's':
    ani.event_source.stop()
    # fig.savefig('test.png')
    plt.savefig(f"{figname}_graph.pdf")
    print(f"Saved fig at: {figname}.pdf")

    np.save(f"{figname}_temp", nozzle_temp_data)
    np.save(f"{figname}_times", time_data)

    utils.close_printer(ser)

cid = fig.canvas.mpl_connect('key_press_event', save_fig)

plt.show()

# Closing script
utils.close_printer(ser)

