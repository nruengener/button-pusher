#include "interpolation.h"
#include "configuration.h"
#include "command.h"

void Interpolation::setCurrentPos(float px, float py, float pz, float pe) {
    Point p;
    p.xmm = px;
    p.ymm = py;
    p.zmm = pz;
    p.emm = pe;
    setCurrentPos(p);
}

int Interpolation::setInterpolation(float px, float py, float pz, float pe, float v) {
    Point p;
    p.xmm = px;
    p.ymm = py;
    p.zmm = pz;
    p.emm = pe;
    return setInterpolation(p, v);
}

int
Interpolation::setInterpolation(float p1x, float p1y, float p1z, float p1e, float p2x, float p2y, float p2z, float p2e,
                                float v) {
    Point p1;
    Point p2;
    p1.xmm = p1x;
    p1.ymm = p1y;
    p1.zmm = p1z;
    p1.emm = p1e;
    p2.xmm = p2x;
    p2.ymm = p2y;
    p2.zmm = p2z;
    p2.emm = p2e;
    return setInterpolation(p1, p2, v);
}

void Interpolation::setCurrentPos(Point p) {
    xStartmm = p.xmm;
    yStartmm = p.ymm;
    zStartmm = p.zmm;
    eStartmm = p.emm;
    xDelta = 0;
    yDelta = 0;
    zDelta = 0;
    eDelta = 0;
}

int Interpolation::setInterpolation(Point p1, float v) {
    Point p0;
    p0.xmm = xStartmm + xDelta;
    p0.ymm = yStartmm + yDelta;
    p0.zmm = zStartmm + zDelta;
    p0.emm = eStartmm + eDelta;
    return setInterpolation(p0, p1, v);
}

int Interpolation::setInterpolation(Point p0, Point p1, float av) {
    if (p1.xmm > UPPER_LIMIT_X || p1.xmm < LOWER_LIMIT_X || p1.ymm > UPPER_LIMIT_Y || p1.ymm < LOWER_LIMIT_Y ||
        p1.zmm > UPPER_LIMIT_Z || p1.zmm < LOWER_LIMIT_Z) {
        printOutOfReach();
        return 1;
    }

    float a = (p1.xmm - p0.xmm);
    float b = (p1.ymm - p0.ymm);
    float c = (p1.zmm - p0.zmm);
    float e = abs(p1.emm - p0.emm);
    float dist = sqrt(a * a + b * b + c * c);
    if (dist < e) {
        dist = e;
    }

    if (av > 0) { // use value of serial command if provided
        v = av; //mm/s
    } else {
//        if (v < 5) { //includes 0 = default value
//            v = sqrt(dist) * 10; //set a good value for v
//        }
        v = sqrt(dist) * 10; //set a good value for v
        if (v < 5) {
            v = 5;
        }
    }

    // todo: serial command for max speed?
    if (v > 90) {
        v = 90;
    }

    tmul = v / dist;

    xStartmm = p0.xmm;
    yStartmm = p0.ymm;
    zStartmm = p0.zmm;
    eStartmm = p0.emm;

    xDelta = (p1.xmm - p0.xmm);
    yDelta = (p1.ymm - p0.ymm);
    zDelta = (p1.zmm - p0.zmm);
    eDelta = (p1.emm - p0.emm);

    state = 0;

    startTime = micros();

    return 0;
}

void Interpolation::updateActualPosition() {
    if (state != 0) {
        return;
    }

    long microsek = micros();
    float t = (microsek - startTime) / 1000000.0;

    //ArcTan Approx.
    /*float progress = atan((PI * t * tmul) - (PI * 0.5)) * 0.5 + 0.5;
    if (progress >= 1.0) {
      progress = 1.0;
      state = 1;
    }*/

    //Cosin Approx.
    float progress = -cos(t * tmul * PI) * 0.5 + 0.5;
    if ((t * tmul) >= 1.0) {
        progress = 1.0;
        state = 1;
        fcallback(); // execute callback
    }

    // synchrone PTP-Bahnplanung!
    xPosmm = xStartmm + progress * xDelta;
    yPosmm = yStartmm + progress * yDelta;
    zPosmm = zStartmm + progress * zDelta;
    ePosmm = eStartmm + progress * eDelta;
}

bool Interpolation::isFinished() const {
    return state != 0;
}

float Interpolation::getXPosmm() const {
    return xPosmm;
}

float Interpolation::getYPosmm() const {
    return yPosmm;
}

float Interpolation::getZPosmm() const {
    return zPosmm;
}

float Interpolation::getEPosmm() const {
    return ePosmm;
}

Point Interpolation::getPosmm() const {
    Point p;
    p.xmm = xPosmm;
    p.ymm = yPosmm;
    p.zmm = zPosmm;
    p.emm = ePosmm;
    return p;
}

float Interpolation::getDistance() const {

}
