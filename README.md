# Elevator Button Pushing System
This project contains the software for a sample mechatronic assistance system which tries to recognize and push elevator buttons.
Control of the used robot arm is to be found in the project 'robot_arm_firmware', the main control routine which contains image processing and detection logic is
contained in the project 'logic_controller'.

## Robot Control
The software is meant to be executed on an Arduino UNO which is connected to a CNC Shield.
The motors of the robot arm are connected to the drivers which are placed on the CNC Shield.
The software is written in C/C++ and can be uploaded to the microcontroller e.g. with the Arduino IDE.

'robotArm' contains the main routine with setup and control loop. It calls the other components as required.
Where 'fk' is responsible for the calculations for the forward kinematics, 'ik' does the same for the inverse kinematics.
The current state of the robot arm position, speed and target in cartesian coordinates is maintained in 'interpolation', where calculations for the cartesian movements are taken. 
Actual robot geometry like angles of the arm parts and reachability of cartesian positions are handled by 'robotGeometry'.
'command' reads G-Code commands from the serial port and interprets them. Responses are written back to the serial port.
Motor control is realized in 'RampsStepper', the endstop is accessed via the 'endstop' module.

## Main Control
The main control software is written in Python and executed on a Raspberry Pi 3 in the test setup.
It contains the logic for image processing, object and text detection, distance calculations and object tracking.
Starting point is 'main' which contains the main control cycle and calls the other modules.
The main functions are separated in different Python packages corresponding to their names.

If the application is not to be started manually via command line it has to be installed as a service on the Raspberry Pi 3.