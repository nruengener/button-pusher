//
// Created by Nando Rüngener on 11.04.2018.
//

#include "endstop.h"
#include "pinout_cnc_shield.h"
#include "Arduino.h"
#include <Bounce2.h>

Bounce bouncerEndstop;

bool initEndstop() {
    pinMode(MOTOR_Y_ENDSTOP, INPUT_PULLUP);
    bouncerEndstop = Bounce();
    bouncerEndstop.attach(MOTOR_Y_ENDSTOP);
    bouncerEndstop.interval(5);
}

// check the limit switch
bool checkEndstop() {
    bouncerEndstop.update();

    if (bouncerEndstop.rose()) { // low to high
        return true;
    }

    return false;
}


