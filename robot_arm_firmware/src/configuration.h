//
// Created by Wohn on 24.03.2018.
//

#ifndef ROBOTARM_CONFIGURATION_H
#define ROBOTARM_CONFIGURATION_H

// uncomment to use limit switches (not fully implemented yet)
//#define ENDSTOPS

#define MICRO_STEPS 16
#define WHOLE_STEPS_PER_TURN 200
#define STEPS_PER_TURN WHOLE_STEPS_PER_TURN * MICRO_STEPS
// Steps per degree stepper gear
#define STEPS_PER_DEGREE_STEPPERGEAR 1.0d * STEPS_PER_TURN / 360
#define GEAR_RATIO_ARMS 47.0 / 19
#define GEAR_RATIO_BASE 108.0 / 19
#define GEAR_STEPPER_TEETH 19.0f
#define GEAR_ARM_TEETH 47.0f
#define GEAR_BASE_TEETH 108.0f

// Steps per degree for right and left arm
#define STEPS_PER_DEGREE_ARMS STEPS_PER_DEGREE_STEPPERGEAR * GEAR_RATIO_ARMS
// Steps per degree for base
#define STEPS_PER_DEGREE_BASE STEPS_PER_DEGREE_STEPPERGEAR * GEAR_RATIO_BASE

// length of arms in mm (joint to joint)
#define LENGTH_ARM1 135.0
#define LENGTH_ARM2 147.0  // 145
#define LENGTH_GRIPPER 88.0  // 87

#define START_X 0
//#define START_Y 146 // best: 146 and 66    142    // 140
//#define START_Z 66  // 63         //  55
#define START_Y 144 // best: 146 and 66    142    // 140
#define START_Z 64  // 63         //  60

#define START_ANGLE_LOW 2.23
#define START_ANGLE_HIGH -0.37

#define ACCELERATION 4000
#define MAX_SPEED 500

// cartesian limits
#define UPPER_LIMIT_X LENGTH_ARM2 + LENGTH_GRIPPER
#define LOWER_LIMIT_X -(LENGTH_ARM2 + LENGTH_GRIPPER)
#define UPPER_LIMIT_Y LENGTH_ARM2 + LENGTH_GRIPPER + 103
//#define LOWER_LIMIT_Y START_Y - LENGTH_GRIPPER
#define LOWER_LIMIT_Y START_Y
#define UPPER_LIMIT_Z LENGTH_ARM1 + 35
#define LOWER_LIMIT_Z -15

// joint angle limits
#define UPPER_LIMIT_LOW 2.265 // shoulder 235
#define LOWER_LIMIT_LOW 0.425 // 0.635
#define UPPER_LIMIT_HIGH 0.375 // elbow
#define LOWER_LIMIT_HIGH -0.75  // -0.37
#define LOWER_LIMIT_BASE -1.5708
#define UPPER_LIMIT_BASE 1.5708

// camera (todo: remove this here, is used on PI side)
#define FOCAL_LENGTH 3.60 // v2: 3.04 mm

#define V_DEFAULT = 40.0

#endif //ROBOTARM_CONFIGURATION_H
