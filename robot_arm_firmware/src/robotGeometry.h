#ifndef ROBOTGEOMETRY_H_
#define ROBOTGEOMETRY_H_

#include "command.h"

class RobotGeometry {
public:
  RobotGeometry();
  int set(float axmm, float aymm, float azmm);
  float getXmm() const;
  float getYmm() const;
  float getZmm() const;
  float getRotRad() const;
  float getLowRad() const;
  float getHighRad() const;
  bool isReachable(float xmm, float ymm, float zmm);
  bool isReachable(Command cmd);
private:
  int calculateGrad();
  float xmm;
  float ymm;
  float zmm;
  float rot;
  float low;
  float high;
};

#endif

