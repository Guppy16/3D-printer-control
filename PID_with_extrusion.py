from asyncio import sleep
import time
from cv2 import repeat
import serial
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import utils


com = "COM6"
figname = f"./PID_tests/EXTRUDE_test_2_{time.time()}"

# Connect to printer
ser = utils.get_serial_connection(port=com, baudrate=38400)

# Define initial parameters
max_start_temp = 25
temp_target = 200
kp = 33
ki = 0.04
kd = 67.8

# Set PID control values
ser.write(f"M301 P{kp} I{ki} D{kd}\r\n".encode())
time.sleep(2)

timestep = 0.5 # seconds
max_timesteps = 60*10 # seconds
avg_pts = 10  # Number of points for moving average


# Setup figure
fig, ax = plt.subplots()
plt.subplots_adjust(right=0.75)
line,= ax.plot([],[], label="T_Nozzle")
target_line, = ax.plot([],[], label="T_Target")
extrude_line, = ax.plot([],[], label="Feed Rate")
# extr_annotation = ax.annotate(f"{avg_pts} Moving Average: ", xy=(1,0))
# extr_avg_text = ax.text(1.04, 0.5, f"{avg_pts} Moving Average: ")

# extr_avg_text = plt.figtext(0.1, 0.5, f"{avg_pts} Moving Average: ", fontsize=14)
textstr = f"{avg_pts} point Avg"
extr_avg_text = plt.gcf().text(0.77, 0.5, textstr, fontsize=12)

ax.set_ylabel("Nozzle Temp")
ax.set_xlabel('Time')
ax.legend(bbox_to_anchor=(1.04,1), loc="upper left")

nozzle_temp_data = np.array([])
time_data = np.array([])
# target_data = np.array([])
extrude_data = np.array([])

# Set extrusion type as absolute
ser.write(f"M83\r\n".encode())

extrude_phase = 0
def extrude_update():
  """Function to send targets"""
  global extrude_data, extrude_phase
  while True:
    # Phase 0: Preheat nozzle to 200 (see default case)

    # Phase 1: Send a step disturbance
    if extrude_phase == 1:
      feed_rate = 360 # mm/min
      extrude_amount = int(feed_rate * timestep / 60)
      ser.write(f"G1 F{feed_rate} E{extrude_amount}\r\n".encode())
      yield feed_rate
      # extrude_data = np.append(extrude_data, [feed_rate])
    
    # Default phase: Extrude 0
    else:
      extrude_phase = 0 # Reset extrude phase
      ser.write(f"G1 F350 E0\r\n".encode())
      yield 0
extrude_update_gen = extrude_update()

rescale_flag = False
axis_start_time = 0
def update(i):
  global nozzle_temp_data, time_data, extrude_data, axis_start_time

  # Read temperature measurement
  # NOTE: This measurement lags behind by 0.5s (i.e. update interval)
  nozzle_temp_data = np.append(nozzle_temp_data, [utils.extract_nozzle_temp(ser)])
  time_data = np.append(time_data, [len(time_data) * timestep])
  extrude_data = np.append(extrude_data, [next(extrude_update_gen)])

  # Replot line
  line.set_data(time_data, nozzle_temp_data)
  target_line.set_data(time_data, [temp_target for _ in time_data])
  extrude_line.set_data(time_data, extrude_data)

  # Plot moving average
  avg_temp = np.mean(nozzle_temp_data[-avg_pts:])
  extr_avg_text.set_text(f"{textstr}\n{avg_temp:.2f}")
  # extr_avg_text.set_position((1.04, 0.5))

  # Rescale axis to show close up view of data
  if rescale_flag:
    axis_start_time = time_data[-1] if axis_start_time == 0 else axis_start_time
    ax.set_xlim(axis_start_time, time_data[-1])
    ax.set_ylim(temp_target - 5, temp_target + 5)
  else:
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
  global extrude_phase, rescale_flag
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

  if event.key == 'r':
    rescale_flag = not rescale_flag
    print(f"Rescaling axis")

cid = fig.canvas.mpl_connect('key_press_event', save_fig)

plt.show()

# Closing script
utils.close_printer(ser)

