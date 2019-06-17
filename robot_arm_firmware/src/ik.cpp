/* Inverse kinetics, Nick Moriarty May 2014
This code is provided under the terms of the MIT license.

The MIT License (MIT)

Copyright (c) 2014 Nick Moriarty

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
 */
#include "math.h"
#include "ik.h"
#include "configuration.h"

const float PI=3.14159265359;

// You can work in any units, as long as they all match; these
// will dictate the units of the 3D space you're in.  I used millimetres.
float L1=LENGTH_ARM1; //Shoulder to elbow length
float L2=LENGTH_ARM2; //Elbow to wrise length
float L3=LENGTH_GRIPPER;  //Length from wrist to hand PLUS base centre to shoulder

// Get polar coords from cartesian ones
void cart2polar(float a, float b, float& r, float& theta)
{
    // Determine magnitude of cartesian coords
    r = sqrt(a*a + b*b);

    // Don't try to calculate zero-magnitude vectors' angles
    if(r == 0) return;

    float c = a / r;
    float s = b / r;

    // Safety!
    if(s > 1) s = 1;
    if(c > 1) c = 1;
    if(s < -1) s = -1;
    if(c < -1) c = -1;

    // Calculate angle in 0..PI
    theta = acos(c);

    // Convert to full range
    if(s < 0) theta *= -1;
}

// Get angle from a triangle using cosine rule
bool cosangle(float opp, float adj1, float adj2, float& theta)
{
    // Cosine rule:
    // C^2 = A^2 + B^2 - 2*A*B*cos(angle_AB)
    // cos(angle_AB) = (A^2 + B^2 - C^2)/(2*A*B)
    // C is opposite
    // A, B are adjacent
    float den = 2*adj1*adj2;

    if(den==0) return false;
    float c = (adj1*adj1 + adj2*adj2 - opp*opp)/den;
    if(c>1 || c<-1) return false;

    // für kleine Winkel ist acos un genau -> atan2
    theta = atan2(sqrt(1 - c * c), c);

//  theta = acos(c);

    return true;
}

// Solve angles!
bool solve(float x, float y, float z, float& a0, float& a1, float& a2)
{
    // Solve top-down view
    float r, th0;
    cart2polar(y, x, r, th0);  // th0 is angle between r and y

    // Account for the wrist length!
    r -= L3;

    // In arm plane, convert to polar
    float ang_P, R;
    cart2polar(r, z, R, ang_P);  // ang_p is angle to horizontal (between R and r)

    // Solve arm inner angles as required
    float B, C;
    if(!cosangle(L2, L1, R, B)) return false;  // B is angle between lower arm and |base to wrist|
    if(!cosangle(R, L1, L2, C)) return false;  // C is angle between lower and upper arm

    // Solve for motor angles from horizontal
    a0 = th0;
    a1 = ang_P + B;
    a2 = C + a1 - PI;

    return true;
}