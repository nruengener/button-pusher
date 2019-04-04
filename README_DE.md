Deutsch | [English](README.md)

# Button Pusher    
Der Button Pusher ist ein (sehr fr�her) Prototyp eines Roboterarms, welcher mit Hilfe von Methoden der KI Fahrstuhlkn�pfe erkennt und bet�tigt.
Es existieren zwei separate Ordner f�r die in C / C ++ geschriebene Firmware des verwendeten Roboterarms sowie die in Python geschriebene Logik des Hauptcontrollers, der auch 
f�r die Bildverarbeitung zust�ndig ist. Details zur Motivation, Konzeption und Umsetzung finden sich in der [Ausarbeitung](Ausarbeitung.pdf).

*Andere Sprachen: [English](README.md), [Deutsch](README_DE.md).*

## Motivation
F�r Menschen mit Behinderung k�nnen scheinbar allt�gliche Aufgaben zu einer gro�en Herausforderung werden. So ist es f�r Menschen mit 
eingeschr�nkter Motorik der Finger, H�nde und Arme schwierig, aus einem Glas zu trinken oder ein Buch aus einem Regal zu nehmen. Technische Assistenzsysteme, 
wie z. B. ein auf einen Rollstuhl montierter Roboterarm sollen hier Abhilfe schaffen. Werden diese Systeme allerdings direkt gesteuert, bspw. mittels Joystick, 
k�nnen Alltagshandlungen immernoch sehr langwierig sein.

In letzter Zeit findet zunehmend Forschung an teilautonomen Assistenzsystemen statt, welche einzelne Handlungsschritte und Bewegungsabl�ufe automatisieren.
In diesem Projekt soll ein Prototyp f�r ein solches System f�r die Funktion der Fahrstuhltasterbet�tigung implementiert werden.

## Beispiel

... Video(s) und Foto(?)

## Komponenten
Als Roboterarm wird ein Modell eines ABB IRB 460 mit Schrittmotoren verwendet (https://www.thingiverse.com/thing:2520572 von Nutzer jackyltle, Lizenz: https://creativecommons.org/licenses/by-nc/3.0/legalcode),
welches eine Abwandlung des EEZYbotARM MK2 (https://www.thingiverse.com/thing:1454048 von Nutzer daGHIZmo, Lizenz: https://creativecommons.org/licenses/by-nc/3.0/legalcode) ist.
Die Steuerung bzw. Firmware f�r den Arm basiert auf https://github.com/ftobler/robotArm (Lizenz: https://creativecommons.org/licenses/by-nc/3.0/legalcode).

Eine detaillierte Liste der verwendeten Komponenten ist in der [Ausarbeitung](Ausarbeitung.pdf) zu finden.