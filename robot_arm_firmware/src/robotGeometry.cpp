#include "robotGeometry.h"
#include <math.h>
#include <Arduino.h>
#include "configuration.h"
#include "command.h"
#include "ik.h"

double d_Min = 85; // 15
double d_Max = 250; // 155

RobotGeometry::RobotGeometry() {

}

int RobotGeometry::set(float axmm, float aymm, float azmm) {
    if (axmm > UPPER_LIMIT_X || axmm < LOWER_LIMIT_X || aymm > UPPER_LIMIT_Y || aymm < LOWER_LIMIT_Y ||
        azmm > UPPER_LIMIT_Z || azmm < LOWER_LIMIT_Z) {
        return 1;
    }

    xmm = axmm;
    ymm = aymm;
    zmm = azmm;
    return calculateGrad();
}

float RobotGeometry::getXmm() const {
    return xmm;
}

float RobotGeometry::getYmm() const {
    return ymm;
}

float RobotGeometry::getZmm() const {
    return zmm;
}

float RobotGeometry::getRotRad() const {
    return rot;
}

float RobotGeometry::getLowRad() const {
    return low;
}

float RobotGeometry::getHighRad() const {
    return high;
}

// todo: optimize code to not calculate angles twice (in isReachable), or check command before pushing it to queue
int RobotGeometry::calculateGrad() {
    float base, shoulder, elbow;

    if (!solve(xmm, ymm, zmm, base, shoulder, elbow)) {
//        Serial.println("not solvable");
        return 2;
    }
    if (shoulder < LOWER_LIMIT_LOW || shoulder > UPPER_LIMIT_LOW || elbow < LOWER_LIMIT_HIGH ||
        elbow > UPPER_LIMIT_HIGH) {
//        Serial.println("joint angles not possible");
//        Serial.print("shoulder: ");
//        Serial.println(shoulder);
//        Serial.print("elbow: ");
//        Serial.println(elbow);
        return 2;
    }

    high = elbow;
    low = shoulder;
    rot = base;

    return 0;
}

bool RobotGeometry::isReachable(Command cmd) {
    float x, y, z;
    if (cmd.getCmd().id != 'H') {
        return true; // home command is always reachable, motor on/of does not matter
    }
    if (cmd.getCmd().num == 0) {
        // absolute
        x = cmd.getCmd().valueX;
        y = cmd.getCmd().valueY;
        z = cmd.getCmd().valueZ;
    } else if (cmd.getCmd().num == 1) {
        // relative
        x = xmm + cmd.getCmd().valueX;
        y = ymm + cmd.getCmd().valueY;
        z = zmm + cmd.getCmd().valueZ;
    } else if (cmd.getCmd().num == 2) {
        // at the moment only base rotation is implemented
        // todo: implement for rotation?
        return true;
    }

    return isReachable(x, y, z);
}


// check if cartesian coordinates are in range and joint angles are valid
bool RobotGeometry::isReachable(float xmm, float ymm, float zmm) {
    float base, shoulder, elbow;
    if (!solve(xmm, ymm, zmm, base, shoulder, elbow)) {
        Serial.println("not solvable");
        Serial.println(base);
        Serial.println(shoulder);
        Serial.println(elbow);
        return false;
    }
    if (shoulder < LOWER_LIMIT_LOW || shoulder > UPPER_LIMIT_LOW || elbow < LOWER_LIMIT_HIGH ||
        elbow > UPPER_LIMIT_HIGH) {
        Serial.println("angles out of range");
        Serial.println(shoulder);
        Serial.println(elbow);
        return false;
    }

    return true;
}
