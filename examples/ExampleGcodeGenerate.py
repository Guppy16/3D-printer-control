import numpy as np
from ProcessCommands import processgcode  # This function edits the gcode

printcommands = np.load('objectdata/HollowCube.npy')  # The hollow cube is chosen for processing

# See the instruction document for details of the following function's inputs
processgcode('OUTPUT_HollowCube', printcommands, nozzletemp=[200, 220, 200], bedtemp=[65, 50], retraction=3)
# The output file is saved as 'OUTPUT_HollowCube' in the outputgcode folder.
# The nozzle temperature starts at 200C, increases to 220 by the middle of the print, then returns to 200C.
# The bed temperature starts at 65C and linearly decreases to 50C.
# The retraction length is set to a constant value of 3mm.
# All other variables are kept as their constant defaults.

print('Data Processed')
