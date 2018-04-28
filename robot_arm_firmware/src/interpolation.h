#ifndef INTERPOLATION_H_
#define INTERPOLATION_H_

#include "arduino.h"

struct Point {
    float xmm;
    float ymm;
    float zmm;
    float emm;
};

// callback that gets called if the the interpolator has finished
typedef void (*finished_callback)(void);

class Interpolation {
public:
    Interpolation(finished_callback fc)
    {
        fcallback = fc;
    }

    //void resetInterpolation(float px, float py, float pz);
    //void resetInterpolation(float p1x, float p1y, float p1z, float p2x, float p2y, float p2z);
    //void resetInterpolation(Point p0, Point p1);

    void setCurrentPos(float px, float py, float pz, float pe);

    int setInterpolation(float px, float py, float pz, float pe, float v = 0);

    int setInterpolation(float p1x, float p1y, float p1z, float p1e, float p2x, float p2y, float p2z, float p2e,
                         float av = 0);

    void setCurrentPos(Point p);

    int setInterpolation(Point p1, float v = 0);

    int setInterpolation(Point p0, Point p1, float v = 0);

    void updateActualPosition();

    bool isFinished() const;

    float getXPosmm() const;

    float getYPosmm() const;

    float getZPosmm() const;

    float getEPosmm() const;

    Point getPosmm() const;

private:
    float getDistance() const;

    byte state;

    long startTime;

    float xStartmm;
    float yStartmm;
    float zStartmm;
    float eStartmm;
    float xDelta;
    float yDelta;
    float zDelta;
    float eDelta;
    float xPosmm;
    float yPosmm;
    float zPosmm;
    float ePosmm;
    float v;
    float tmul;

    finished_callback fcallback;
};

#endif
