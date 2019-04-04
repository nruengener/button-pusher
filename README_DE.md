Deutsch | [English](README.md)

# Button Pusher    
Der Button Pusher ist ein (sehr früher) Prototyp eines Roboterarms, welcher mit Hilfe von Methoden der KI Fahrstuhlknöpfe erkennt und betätigt.
Es existieren zwei separate Ordner für die in C / C ++ geschriebene Firmware des verwendeten Roboterarms sowie die in Python geschriebene Logik des Hauptcontrollers, der auch 
für die Bildverarbeitung zuständig ist. Details zur Motivation, Konzeption und Umsetzung finden sich in der [Ausarbeitung](Ausarbeitung.pdf).

*Andere Sprachen: [English](README.md), [Deutsch](README_DE.md).*

## Motivation
Für Menschen mit Behinderung können scheinbar alltägliche Aufgaben zu einer großen Herausforderung werden. So ist es für Menschen mit 
eingeschränkter Motorik der Finger, Hände und Arme schwierig, aus einem Glas zu trinken oder ein Buch aus einem Regal zu nehmen. Technische Assistenzsysteme, 
wie z. B. ein auf einen Rollstuhl montierter Roboterarm sollen hier Abhilfe schaffen. Werden diese Systeme allerdings direkt gesteuert, bspw. mittels Joystick, 
können Alltagshandlungen immernoch sehr langwierig sein.

In letzter Zeit findet zunehmend Forschung an teilautonomen Assistenzsystemen statt, welche einzelne Handlungsschritte und Bewegungsabläufe automatisieren.
In diesem Projekt soll ein Prototyp für ein solches System für die Funktion der Fahrstuhltasterbetätigung implementiert werden.

## Beispiel

... Video(s) und Foto(?)

## Komponenten
Als Roboterarm wird ein Modell eines ABB IRB 460 mit Schrittmotoren verwendet (https://www.thingiverse.com/thing:2520572 von Nutzer jackyltle, Lizenz: https://creativecommons.org/licenses/by-nc/3.0/legalcode),
welches eine Abwandlung des EEZYbotARM MK2 (https://www.thingiverse.com/thing:1454048 von Nutzer daGHIZmo, Lizenz: https://creativecommons.org/licenses/by-nc/3.0/legalcode) ist.
Die Steuerung bzw. Firmware für den Arm basiert auf https://github.com/ftobler/robotArm (Lizenz: https://creativecommons.org/licenses/by-nc/3.0/legalcode).

Eine detaillierte Liste der verwendeten Komponenten ist in der [Ausarbeitung](Ausarbeitung.pdf) zu finden.