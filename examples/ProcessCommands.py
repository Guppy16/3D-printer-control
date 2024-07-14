import numpy as np
from scipy import interpolate


def interpolate_variable(variable, length):
    # Interpolation functions map length of input variable to length of gcode file
    if np.isscalar(variable):  # Variable is constant throughout print
        f = interpolate.interp1d([0, length-1], [variable, variable])
    else:  # Interpolate variable over print
        f = interpolate.interp1d(np.linspace(0, length-1, len(variable)), variable)
    return f


def addvariable(command, index, string):
    # Returns gcode string if the variable value is defined in command
    if np.isnan(command[index]):
        return ''
    else:
        return ' ' + string + str(command[index])


def processgcode(filestub, commands, kp=15.5, ki=0.13, kd=6.0, nozzletemp=210, bedtemp=55, speedfactor=1,
                 extrusionfactor=1, retraction=2.5, fanspeed=255):

    # Safety limits: to prevent damage to the printer
    assert 190 <= nozzletemp <= 260
    assert bedtemp <= 75
    assert extrusionfactor <= 2
    assert retraction <= 15

    # Create interpolation functions
    fkp = interpolate_variable(kp, len(commands))
    fki = interpolate_variable(ki, len(commands))
    fkd = interpolate_variable(kd, len(commands))
    fnozzletemp = interpolate_variable(nozzletemp, len(commands))
    fbedtemp = interpolate_variable(bedtemp, len(commands))
    fspeedfactor = interpolate_variable(speedfactor, len(commands))
    fextrusionfactor = interpolate_variable(extrusionfactor, len(commands))
    fretraction = interpolate_variable(retraction, len(commands))
    ffanspeed = interpolate_variable(fanspeed, len(commands))

    # All gcode is saved in output variable, which is saved to file at the end
    output = 'M301 P' + str(fkp(0)) + ' I' + str(fki(0)) + ' D' + str(fkd(0)) + '\n'  # Set initial PID parameters
    output += 'M140 S' + str(fbedtemp(0)) + '\n' + 'M190 S' + str(fbedtemp(0)) + '\n'  # Set initial bed temperature
    output += 'M104 S' + str(fnozzletemp(0)) + '\n' + 'M109 S' \
              + str(fnozzletemp(0)) + '\n'  # Set initial hotend temperature
    output += 'M83\nG21\nG90\nM107\nG28\nG0 Z5 E5 F500\nG0 X-1 Z0\nG1' \
              ' Y60 E3 F500\nG1 Y10 E8 F500\nG1 E-1 F250\n'  # Initialise printer

    # Retract, move to starting position, and begin extrusion
    output += 'G1 F2400 E-2.5\nG0'
    output += addvariable(commands[0], 2, 'X')  # Add X command if it exists
    output += addvariable(commands[0], 3, 'Y')  # Add Y command if it exists
    output += addvariable(commands[0], 4, 'Z')  # Add Z command if it exists
    output += addvariable(commands[0], 5, 'E')  # Add E command if it exists
    output += '\nG1 F2400 E2.5\n'

    output += 'M106 S' + str(ffanspeed(0)) + '\n'  # Set initial fan speed

    # Walk through all remaining commands
    for i in range(2, len(commands)):
        if i % 1000 == 0:
            print(str(i) + '/' + str(len(commands)) + ' commands')
        commands[i][1] *= fspeedfactor(i) # Apply speed factor
        if commands[i][5] < 0:
            commands[i][5]= -fretraction(i) # Apply retraction
        elif commands[i-1][5] < 0:
            commands[i][5] = fretraction(i) # Apply retraction
        else:
            commands[i][5] *= fextrusionfactor(i) # Apply extrusion factor

        # Change PID controls when necessary
        if float(fkp(i)) != float(fkp(i-1)) or float(fki(i)) != float(fki(i-1)) or float(fkd(i)) != float(fkd(i-1)):
            output += 'M301 P' + str(fkp(i)) + ' I' + str(fki(i)) + ' D' + str(fkd(i)) +'\n'
        # Change hotend temperature when necessary
        if float(fnozzletemp(i)) != float(fnozzletemp(i-1)):
            output += 'M104 S' + str(fnozzletemp(i)) + '\n'
        # Change bed temperature when necessary
        if float(fbedtemp(i)) != float(fbedtemp(i-1)):
            output += 'M140 S' + str(fbedtemp(i)) + '\n'
        # Change fan speed when necessary
        if float(ffanspeed(i)) != float(ffanspeed(i-1)):
            output += 'M106 S' + str(ffanspeed(i)) + '\n'

        output += 'G' + str(int(commands[i][0]))
        output += addvariable(commands[i], 2, 'X')  # Add X command if it exists
        output += addvariable(commands[i], 3, 'Y')  # Add Y command if it exists
        output += addvariable(commands[i], 4, 'Z')  # Add Z command if it exists
        output += addvariable(commands[i], 5, 'E')  # Add E command if it exists
        output += '\n'

    # Closing code
    output += 'M107\nG0 X0 Y120\nM190 S0\nG1 E-3 F200\nM104 S0\nG4 S300\nM107\nM84'

    # Write output to file
    filename = 'outputgcode/' + filestub + '.gcode'
    file = open(filename, 'w')
    file.write(output)
    file.close()