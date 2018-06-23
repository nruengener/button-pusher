#include "pinout_cnc_shield.h"
#include "robotGeometry.h"
#include "interpolation.h"
#include "rampsStepper.h"
#include "queue.h"
#include "command.h"
#include "configuration.h"
#include "fk.h"
#include "endstop.h"
#include "ik.h"

RampsStepper stepperRotate(Z_STEP_PIN, Z_DIR_PIN, Z_ENABLE_PIN);
RampsStepper stepperLower(Y_STEP_PIN, Y_DIR_PIN, Y_ENABLE_PIN);
RampsStepper stepperHigher(X_STEP_PIN, X_DIR_PIN, X_ENABLE_PIN);

void interpolatorFinishedCallback(void) {
    printCommandFinished();
}

RobotGeometry geometry;
Interpolation interpolator(interpolatorFinishedCallback);
Queue<Cmd> queue(5);
Command command;

void executeCommand(Cmd cmd);

void setStepperEnable(bool enable) {
    stepperRotate.enable(enable);
    stepperLower.enable(enable);
    stepperHigher.enable(enable);
}

void setup() {
    Serial.begin(9600);

    initEndstop();

    stepperLower.setInvertDirection(true);
    stepperRotate.setInvertDirection(true);

    //reduction of steppers..
    stepperHigher.setReductionRatio(GEAR_ARM_TEETH / GEAR_STEPPER_TEETH, WHOLE_STEPS_PER_TURN * MICRO_STEPS);
    stepperLower.setReductionRatio(GEAR_ARM_TEETH / GEAR_STEPPER_TEETH, WHOLE_STEPS_PER_TURN * MICRO_STEPS);
    stepperRotate.setReductionRatio(GEAR_BASE_TEETH / GEAR_STEPPER_TEETH, WHOLE_STEPS_PER_TURN * MICRO_STEPS);

    //init interpolation
    setStepperEnable(false);

    Point startPoint;
    startPoint.xmm = 0;
    startPoint.ymm = START_Y;
    startPoint.zmm = START_Z;
    startPoint.emm = 0;
//    interpolator.setCurrentPos(startPoint);
    interpolator.setInterpolation(startPoint, startPoint, 5);

    float base, low, high;
    if (!solve(0, START_Y, START_Z, base, low, high)) {
        Serial.println("error with starting position");
    }
    //start positions of motors
    stepperHigher.setPositionRad(high);
    stepperLower.setPositionRad(low);
    stepperRotate.setPositionRad(base);
    Serial.println(base);
    Serial.println(low);
    Serial.println(high);

//    Serial.println("start");
    delay(10);
}

int result;

void loop() {
    // set home position if endtops reached
    if (checkEndstop()) {
        printEndstopReached();
//        int res = interpolator.setInterpolation(START_X, START_Y, START_Z, 0, 0);
//        if (res > 0) {
//            printFault();
//        }
//        // todo: empty command queue?
//        while (!queue.isEmpty()) {
//            queue.pop();
//        }
//        return;
    }

    //update and Calculate all Positions, Geometry and Drive all Motors...
    interpolator.updateActualPosition();
    result = geometry.set(interpolator.getXPosmm(), interpolator.getYPosmm(), interpolator.getZPosmm());

    stepperRotate.stepToPositionRad(geometry.getRotRad());
    stepperLower.stepToPositionRad(geometry.getLowRad());
    stepperHigher.stepToPositionRad(geometry.getHighRad());

    stepperRotate.update();
    stepperLower.update();
    stepperHigher.update();

    if (!queue.isFull()) {
        if (command.handleGcode()) {
            // only push command to queue if it is in range
            if (geometry.isReachable(command)) {
                queue.push(command.getCmd());
                printOk();
            } else {
                printOutOfReach();
            }
        }
//        else {
//            printErr(); // print er over serial
//        }
    }
    if ((!queue.isEmpty()) && interpolator.isFinished()) {
        executeCommand(queue.pop());
    }

}

void cmdMove(Cmd (&cmd)) {
    if (!geometry.isReachable(cmd.valueX, cmd.valueY, cmd.valueZ)) {
        printOutOfReach();
        Serial.println("cmd: out of range");
//        Serial.println(cmd.valueX);
//        Serial.println(cmd.valueY);
//        Serial.println(cmd.valueZ);
        return;
    }

    interpolator.setInterpolation(cmd.valueX, cmd.valueY, cmd.valueZ, cmd.valueE, cmd.valueF);
}

void cmdMoveRelative(Cmd (&cmd)) {
    float newX, newY, newZ, newE;
    newX = cmd.valueX + interpolator.getXPosmm();
    newY = cmd.valueY + interpolator.getYPosmm();
    newZ = cmd.valueZ + interpolator.getZPosmm();
    newE = cmd.valueE + interpolator.getEPosmm();

    if (!geometry.isReachable(newX, newY, newZ)) {
        printOutOfReach();
        Serial.println("relative cmd: out of range");
//        Serial.println(newX);
//        Serial.println(newY);
//        Serial.println(newZ);
        return;
    }

    interpolator.setInterpolation(newX, newY, newZ, newE, cmd.valueF);
}

// relative turn for given angles around axes
void cmdTurnAngles(Cmd (&cmd)) {
    float newBase, newLower, newHigher, newX, newY, newZ;

    // command sent angles in grad
    float rotZ = cmd.valueZ * DEG_TO_RAD; //0.017453292519943;
    newBase = rotZ + stepperRotate.getPositionRad(); // base turns around z axis

    // todo: implement lower and higher angles
    newLower = stepperLower.getPositionRad();
    newHigher = stepperHigher.getPositionRad();

    if (newBase < LOWER_LIMIT_BASE || newBase > UPPER_LIMIT_BASE) {
        return;
    }

//    Serial.println("old:");
//    Serial.println(interpolator.getXPosmm());
//    Serial.println(interpolator.getYPosmm());
//    Serial.println(interpolator.getZPosmm());

    unsolve(newBase, newLower, newHigher, newX, newY, newZ); // forward kinematics (important if shoulder and elbow are implemented)
    interpolator.setInterpolation(newX, newY, newZ, interpolator.getEPosmm(), cmd.valueF);

//    Serial.println("new:");
//    Serial.println(newX);
//    Serial.println(newY);
//    Serial.println(newZ);
}

void cmdDwell(Cmd (&cmd)) {
    delay(int(cmd.valueT * 1000));
}

void cmdStepperOn() {
    setStepperEnable(true);
}

void cmdStepperOff() {
    setStepperEnable(false);
}

void handleAsErr(Cmd (&cmd)) {
    printComment("Unknown Cmd " + String(cmd.id) + String(cmd.num) + " (queued)");
    printFault();
}

void executeCommand(Cmd cmd) {
    if (cmd.id == -1) {
        String msg = "parsing Error";
        printComment(msg);
        handleAsErr(cmd);
        return;
    }

    if (cmd.valueX == NAN) {
        cmd.valueX = interpolator.getXPosmm();
    }
    if (cmd.valueY == NAN) {
        cmd.valueY = interpolator.getYPosmm();
    }
    if (cmd.valueZ == NAN) {
        cmd.valueZ = interpolator.getZPosmm();
    }
    if (cmd.valueE == NAN) {
        cmd.valueE = interpolator.getEPosmm();
    }

    // todo: home position command working?
    // todo: turn angle z axis command (to center image on object) working?
    //decide what to do
    if (cmd.id == 'G') { // move commands
        switch (cmd.num) {
            case 0:
                cmdMove(cmd);
                break;
            case 1:
                cmdMoveRelative(cmd); // relative move for G1
                break;
            case 2:
                cmdTurnAngles(cmd); // turn around axis for G2
                break;
            case 4:
                cmdDwell(cmd);
                break;
                //case 21: break; //set to mm
                //case 90: cmdToAbsolute(); break;
                //case 91: cmdToRelative(); break;
                //case 92: cmdSetPosition(cmd); break;
            default:
                handleAsErr(cmd);
        }
    } else if (cmd.id == 'M') { // motor on/off commands
        switch (cmd.num) {
            //case 0: cmdEmergencyStop(); break;
            case 17:
                cmdStepperOn();
                break;
            case 18:
                cmdStepperOff();
                break;
            default:
                handleAsErr(cmd);
        }
    } else if (cmd.id == 'H') { // go to home position command
        interpolator.setInterpolation(START_X, START_Y, START_Z, 0, 0); //cmd.valueE, cmd.valueF);
    } else {
        printComment("Unknown id " + String(cmd.id));
        handleAsErr(cmd);
    }
}


