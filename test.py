

extrude_phase = 0
def extrude_update():
  """Function to send targets"""
  global extrude_data
  while True:
    # Phase 0: Preheat nozzle to 200
    if extrude_phase == 0:
      # ser.write(f"G1 F350 E0\r\n".encode())
      yield 0
      # extrude_data = np.append(extrude_data, [0])

    # Phase 1: Send a step disturbance
    if extrude_phase == 1:
      feed_rate = 360
      # ser.write(f"G1 F{feed_rate} E50\r\n".encode())
      yield feed_rate
      # extrude_data = np.append(extrude_data, [feed_rate])

print(next(extrude_update()))