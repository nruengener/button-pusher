#include "command.h"

/**
 * Handles communication over serial port.
 */
Command::Command() {
    //initialize Command to a zero-move value;
    command.valueX = NAN;
    command.valueY = NAN;
    command.valueZ = NAN;
    command.valueF = 0;
    command.valueE = 0;
    command.valueT = 0;

    message = "";
}

bool Command::handleGcode() {
    if (Serial.available()) {
        char c = Serial.read();
//        Serial.print(c);
        if (c == '\n') {
            bool b = processMessage(message);
            message = "";
            return b;
//       return false;
        }
        if (c == '\r') {
            bool b = processMessage(message);
            message = "";
            return b;
        } else {
            message += c;
        }
    }
    return false;
}

bool Command::processMessage(String &msg) {
    if (msg.length() < 1) {
        return false;
    }

    msg += ' ';  //helps parsing
    command.id = msg[0];
    //exit if not GCode
    if ((command.id != 'G') && (command.id != 'M') && (command.id != 'H')) {
        printComment("Command id is not one of G, M or H");
        printComment(message);
        return false;
    }

    //parse number
    int first = 1;
    int last = pos(msg, ' ', 1);
    if (last < 0) {
        printComment("Could not parse command number");
        return false;
    }
    String s = msg.substring(first, last);
    command.num = s.toInt();
    // Serial.println(cmd.num);

    //parse up to 5 Values
    command.valueX = NAN;
    command.valueY = NAN;
    command.valueZ = NAN;
    command.valueE = NAN;
    command.valueF = 0;
    command.valueT = 0;
    int parsePosition = last + 1;
    int i = 0;
    while (i < 5) {
        char id = msg[parsePosition++];
        if (id != ' ') {  //test if a command here
            int first = parsePosition;
            int last = pos(msg, ' ', parsePosition);
            if (last < first) { //test if String is valid
                i = 5; //exit;
            } else {
                String floatString = msg.substring(first, last);  //should contain a Numeric value
                float value = floatString.toFloat();
                switch (id) {
                    case 'X':
                        command.valueX = value;
                        break;
                    case 'Y':
                        command.valueY = value;
                        break;
                    case 'Z':
                        command.valueZ = value;
                        break;
                    case 'E':
                        command.valueZ = value;
                        break;
                    case 'F':
                        command.valueF = value;
                        break;
                    case 'T':
                        command.valueT = value;
                        break;
                    default:
                        i = 5;
                }
                parsePosition = last + 1;
            }
        } else {
            i = 5; //exit;
        }
        i++;
    }

    return true;
}

Cmd Command::getCmd() const {
    return command;
}

int Command::pos(String &s, char c, int start) {
    int len = s.length();
    for (int i = start; i < len; i++) {
        if (c == s[i]) {
            return i;
        }
    }
    return -1;
}


void printErr() {
    Serial.println("rs"); //'resend'
}

void printFault() {
    Serial.println("!!");
}

void printComment(char *c) {
    Serial.print("// ");
    Serial.println(c);
}

void printComment(String &s) {
    Serial.print("// ");
    Serial.println(s);
}

void printOk() {
    Serial.println("ok"); // command accepted
}

void printOutOfReach() {
    Serial.println("or");
}

void printCommandFinished() {
    Serial.println("cf");
}

void printEndstopReached() {
    Serial.println("er");
}