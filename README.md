# Improving 3D Printer Control

We investigate the temperature controller of a 3D printer and reduce the error of its response to a step change in filament extrusion. 

[gif of the error]

Our scripts were run on a Monoprice MP Select Mini 3D Printer. The nozzle is modelled as a linear system as shown in the schematic with basic components:
- Heater/Fan to vary the temperature
- Thermistor to measure the nozzle temperature
- Filament absorbs heat

[insert diagram of linear system. Credits: @sam]

## PID Temperature Controller

[insert Fig 1]

Figure 1 shows the step response of the controller with different controller parameters. These show signs of a normal second order response with a small delay.

[insert Fig 2]

Figure 2 shows the affect of varying Kp (proportional gain) on the response of the system. For values of Kp > 10, we see an expected 
- overshoot which decreases with increasing Kp
- and some steady state error, which decreases with increasing Kp
Interestingly, when Kp is small (Kp ~ 1), we see the non-linearities exacerbate. It is clear that there are two modes of operation - the heater heats up the nozzle, while the fan cools it. This can be better modelled as a MIMO system. 

Conclusion: The PID tune is ok. The system is well approximated as being linear for reasonable PID values. 

## Reducing the error in a step change in feed input

Consider a step input in feed rate, i.e. we are extruding filament at a constant rate. With a normal PID controller, the system displays a second order response to a distrubance at the output as shown below.

[Insert Fig 3]

We used feed forward control (FFC) to anticipate the disturbance, and adjust the setpoint to get a smaller error at the output. The controller is shown below. 

[Fig 4: FF Controller]

We design the FF Controller as follows. Without the FFC, the transfer function from the demand temperature $t_d$ and feedrate $f$ to the nozzle temperature $t$ is:

$\overline{t} = \frac{L(s) \, \overline{t_d} \, + \, D(s) \overline{f}}{1 \, + \, L(s)}$

Consider applying the extra demand $\overline{\delta t_d} = -\frac{D(s)}{L(s)}\overline{f}$. Hence subbing in to the transfer function above $\overline{t_d} \leftarrow \overline{t_d} + \overline{\delta t_d} $ we get:

$\overline{t} = \frac{L(s) \, \overline{t_d} - \frac{D(s)}{L(s)}\overline{f} \, + \, D(s) \overline{f}}{1 \,+\, L(s)} = \frac{L(s)}{1 \, + \, L(s)} \overline{t_d}$

This gives us back the original system with on disturbance! Hence the resulting feedforward control we want to apply is given by $\overline{\delta t_d}$. To estimate the transfer functions, we assume that $L(s)$ is much slower than the disturbance, hence can be approximated as being constant. 



At steady state, 

 we estimated the transfer function of the disturbance as:


The results 


## Files