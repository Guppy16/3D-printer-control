# Utils file
from operator import xor
import serial
import time
import numpy as np

def get_serial_connection(port="COM6", baudrate=38400):
  ser = serial.Serial(port=port, baudrate=baudrate)
  ser.reset_input_buffer()
  ser.reset_output_buffer()
  ser.write(b'\r\n\r\n')
  time.sleep(2)
  ser.reset_input_buffer()
  return ser


def get_nozzle_temp(ser: serial.Serial):
  """Get Nozzle temperature from printer
  NOTE: this waits 0.2s for the printer to get temperature
  """
  # ser.write(b'\r\n\r\n')
  # time.sleep(2)
  ser.reset_input_buffer()
  ser.reset_output_buffer()
  ser.write(b'M105\r\n')
  time.sleep(0.2)
  return extract_nozzle_temp(ser)

  # out = ser.read(ser.in_waiting)
  # out = str(out)
  # print(out)
  # if out != '' and ':' in out and 'S' not in out:
  #   colon = out.find('T:') + 1
  #   return float(out[colon+1:colon+6])
  # return 0.0

def extract_nozzle_temp(ser: serial.Serial):
  """Assuming command has already been sent"""
  out = ser.read(ser.in_waiting)
  out = str(out)
  if out != '' and ':' in out and 'S' not in out:
    colon = out.find('T:') + 1
    return float(out[colon+1:colon+6])
  print("Error: No temperature found")
  return 0.0

def close_printer(ser: serial.Serial, cool=True):
  """Close printer and cool if high temp"""
  if not ser.is_open:
    return
  ser.write(b'M104 S0\r\n')  # Turns off nozzle heater
  print("Nozzle heater off")
  time.sleep(1)
  cool and ser.write(b'M106 S255\r\n') and print("Fans on")  # Start cooling down the nozzle for future PID tests
  ser.close()
  print("Closed serial port")

def turn_on_fans(ser: serial.Serial):
  """Write G-code over serial command to turn on fans"""
  ser.write(b'M42 P9 S255\r\n')
  ser.write(b'M42 P4 S255\r\n')
  ser.write(b'M106 S200\r\n')

def set_nozzle_temp(ser: serial.Serial, temp=25, avg_num=3, tol=0.5):
  """Heat up or cool down nozzle to stable temperature
  Use cases:
  Wait for printer nozzle to cool down to a temperature
  Heat up nozzle to a specific temperature and then monitor

  temp: set temperature
  avg_num: number of timesteps to average temperature
  tol: tolerance
  """

  # Easiest thing to do is to use printer commands
  # But this mau not work:
  # ser.write(f"M104 S{temp}\r\n".encode())

  # Initialise array of temperature moving avgs
  moving_avg_temps = np.array([get_nozzle_temp(ser) for _ in range(avg_num)])
  avg_temp = np.mean(moving_avg_temps)

  if abs(avg_temp - temp) <= tol:
    print("Already at required temperature")
    return True
    
  # Flag to turn on fan if cooling nozzle
  flag_cooling = avg_temp > temp

  if avg_temp < temp:   # Heat printer
    ser.write(f"M104 S{temp}\r\n".encode())

  # Create checkpoints
  temperature_checkpoints = np.linspace(avg_temp, temp, num=10)

  while abs(moving_avg_temps[-1] - temp) < tol:
    # Update moving avg
    # NOTE: circular array implementation will be less memory intense
    moving_avg_temps = np.append(moving_avg_temps, [get_nozzle_temp(ser)])
    avg_temp = np.mean(moving_avg_temps[-avg_num:])

    # Pretty neat use of XOR
    if flag_cooling ^ avg_temp > temperature_checkpoints[-1]:
        print(f"Moving Avg Temp: {avg_temp}")
        temperature_checkpoints.pop()

    # Turn on fan if needed
    flag_cooling and turn_on_fans(ser)
  
  # Return
  print(f"Reached desired tolerance: {avg_temp}")

if __name__ == "__main__":
  ser = get_serial_connection()
  try:
    val = get_nozzle_temp(ser)
    print(val)
  finally:
    close_printer(ser, cool=False)