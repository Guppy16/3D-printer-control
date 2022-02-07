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
extrude_line, = ax.plot([],[], label="Feed Rate")
ax.set_ylabel("Nozzle Temp")
ax.set_xlabel('Time')
ax.legend()

nozzle_temp_data = np.array([])
time_data = np.array([])
# target_data = np.array([])
extrude_data = np.array([])

# Set extrusion type as absolute
ser.write(f"M83\r\n".encode())

extrude_phase = 0
def extrude_update():
  """Function to send targets"""
  global extrude_data
  while True:
    # Phase 0: Preheat nozzle to 200
    if extrude_phase == 0:
      ser.write(f"G1 F350 E0\r\n".encode())
      yield 0
      # extrude_data = np.append(extrude_data, [0])

    # Phase 1: Send a step disturbance
    if extrude_phase == 1:
      feed_rate = 360
      ser.write(f"G1 F{feed_rate} E50\r\n".encode())
      yield feed_rate
      # extrude_data = np.append(extrude_data, [feed_rate])
extrude_update_gen = extrude_update()

def update(i):
  global nozzle_temp_data, time_data, extrude_data

  # Read temperature measurement
  # NOTE: This measurement lags behind by 0.5s (i.e. update interval)
  nozzle_temp_data = np.append(nozzle_temp_data, [utils.extract_nozzle_temp(ser)])
  time_data = np.append(time_data, [len(time_data) * timestep])
  extrude_data = np.append(extrude_data, [next(extrude_update_gen)])
  
  # print(f"Extrude data", extrude_data)
  # extrude_update()

  # Replot line
  line.set_data(time_data, nozzle_temp_data)
  target_line.set_data(time_data, [temp_target for _ in time_data])
  extrude_line.set_data(time_data, extrude_data)
  ax.autoscale()
  ax.relim()
  ax.autoscale_view()

  # Send command to printer to measure temperature
  ser.write(b'M105\r\n')
    
# Heat up nozzle to desired temperature
# NOTE: MAY want to visualise this to check
# if temperature has truly settled
# utils.set_nozzle_temp(ser, temp=temp_target, avg_num=10, tol=0.5)

# Set desired temperature
ser.write(f"M104 S{temp_target}\r\n".encode())

# Request temperature measurement
ser.write(b'M105\r\n')
ani = animation.FuncAnimation(fig, update, interval=int(timestep*1000), frames=int(max_timesteps/timestep), repeat=False)

def save_fig(event):
  global extrude_phase
  if event.key == 's':
    ani.event_source.stop()
    # fig.savefig('test.png')
    plt.savefig(f"{figname}_graph.pdf")
    print(f"Saved fig at: {figname}.pdf")

    np.save(f"{figname}_temp", nozzle_temp_data)
    np.save(f"{figname}_times", time_data)

    utils.close_printer(ser)
  
  if event.key == 'e':
    extrude_phase += 1
    print(f"Extrude phase: {extrude_phase}")

cid = fig.canvas.mpl_connect('key_press_event', save_fig)

plt.show()

# Closing script
utils.close_printer(ser)

