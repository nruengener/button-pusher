English | [Deutsch](README_DE.md)  

# Button Pusher
The button pusher is a (very early) prototype of a robotic arm, which recognizes and pushes a desired elevator button with the help of AI methods.
There are two separate folders, one for the firmware of the used robot arm written in C/C++ and the other for the logic of the main controller written in Python.

Details on motivation, conception and implementation can be found in the [elaboration](Ausarbeitung.pdf) (only german version available).

*Read this in other languages: [Deutsch](README_DE.md), [English](README.md).*

## Introduction (Motivation)
For people with disabilities, seemingly everyday tasks can become a major challenge. So it is difficult for people with limited motor 
skills of the fingers, hands and arms to drink from a glass or to take a book from a shelf. 
Technical assistance systems, such as a robotic arm mounted on a wheelchair should remedy this situation. 
However, if these systems are controlled directly, for example by means of a joystick, everyday activities can still be very tedious.

Recently, research on semi-autonomous assistance systems, which automate individual steps and sequences of movements, is increasingly taking place.
In this project, a prototype for such a system for the function of the elevator button operation is to be implemented.

## Example
was kann er

## Components
The robot arm used is a model of an ABB IRB 460 with stepper motors (https://www.thingiverse.com/thing:2520572 by user jackyltle, license: https://creativecommons.org/licenses/by-nc/3.0/legalcode),
which is a modification of the EEZYbotARM MK2 (https://www.thingiverse.com/thing:1454048 by user daGHIZmo, license: https://creativecommons.org/licenses/by-nc/3.0/legalcode). 
The control or firmware for the arm is partly based on https://github.com/ftobler/robotArm (license: https://creativecommons.org/licenses/by-nc/3.0/legalcode).

A detailed list of the components used can be found in the [elaboration](Ausarbeitung.pdf) (only german version available).



