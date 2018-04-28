#ifndef PINOUT_H_
#define PINOUT_H_

#define LED_PIN            13

// Motor Pins Arduino Uno with CNC shield
#define STEPPER_ENABLE_PIN 8
#define MOTOR_X_STEP_PIN 2
#define MOTOR_X_DIR_PIN 5 // low = CW, high = CCW?
#define MOTOR_Y_STEP_PIN 3
#define MOTOR_Y_DIR_PIN 6
#define MOTOR_Z_STEP_PIN 4
#define MOTOR_Z_DIR_PIN 7

// End Stops
#define MOTOR_X_ENDSTOP 9 /* X axis endstop input pin */
#define MOTOR_Y_ENDSTOP 10  /* Y axis endstop input pin */
#define MOTOR_Z_ENDSTOP 11  /* Z axis endstop input pin */

#define X_STEP_PIN         2
#define X_DIR_PIN          5
#define X_ENABLE_PIN       8
#define X_MIN_PIN           9
#define X_MAX_PIN           9

#define Y_STEP_PIN         3
#define Y_DIR_PIN          6
#define Y_ENABLE_PIN       8
#define Y_MIN_PIN          9
#define Y_MAX_PIN          9

#define Z_STEP_PIN         4
#define Z_DIR_PIN          7
#define Z_ENABLE_PIN       8
#define Z_MIN_PIN          9
#define Z_MAX_PIN          9

//#define E_STEP_PIN         26
//#define E_DIR_PIN          28
//#define E_ENABLE_PIN       24
//
//#define Q_STEP_PIN         36
//#define Q_DIR_PIN          34
//#define Q_ENABLE_PIN       30
//
//#define SDPOWER            -1
//#define SDSS               53
//#define LED_PIN            13
//
//#define FAN_PIN             9
//
//#define PS_ON_PIN          12
//#define KILL_PIN           -1
//
//#define HEATER_0_PIN       10
//#define HEATER_1_PIN        8
//#define TEMP_0_PIN         13   // ANALOG NUMBERING
//#define TEMP_1_PIN         14   // ANALOG NUMBERING
//
////RAMPS AUX-1
//#define STEPPER_GRIPPER_PIN_0 40
//#define STEPPER_GRIPPER_PIN_1 59
//#define STEPPER_GRIPPER_PIN_2 63
//#define STEPPER_GRIPPER_PIN_3 64
//


#endif
