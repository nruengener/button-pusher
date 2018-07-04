# Elevator Button Pushing System
This project contains the software for a sample mechatronic assistance system which tries to recognize and push elevator buttons.
Control of the used robot arm is to be found in the project 'robot_control???', the main control routine which contains image processing and detection logic is
contained in the project '???'.

## Robot Control
The software is meant to be executed on an Arduino UNO which is connected to a CNC Shield.
The motors of the robot arm are connected to the drivers which are placed on the CNC Shield.
The software is written in C/C++ and can be uploaded to the microcontroller e.g. with the Arduino IDE.

'robotArm.ino' contains the main routine with setup and control loop. It calls the other components as required.
Where 'fk' is responsible for the calculations for the forward kinematics, 'ik' does the same for the inverse kinematics.
The current state of the robot arm position and ??? is maintained in 'interpolation' ...
'command???' reads G-Code commands from the serial port and interprets them. Responses are written back to the serial port.

State of the motors?
Motor commands are executed via '???'





## Main Control
The main control software is written in Python and executed on a Raspberry Pi 3 in the test setup.
It contains the logic for image processing, object and text detection, distance calculations and ...

Starting point is '???'

The main functions are separated in different Python packages corresponding to their names.