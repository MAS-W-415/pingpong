#ifndef BALL_H 
#define BALL_H



#include "raylib.h"
#include "velocity.h"

class Ball 
{
    public:
        float centerX;
        float centerY;
        float radius;
        Color color;
        Velocity v;

        Ball(float x, float y, float r, Color c, Velocity v) : centerX(x), centerY(y), radius(r), color(c), v(v) {;};
        Ball(){;}
        ~Ball() = default;

};

#endif
