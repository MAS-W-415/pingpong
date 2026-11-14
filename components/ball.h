#ifndef BALL_H 
#define BALL_H



#include "raylib.h"
#include "velocity.h"

class Ball 
{
    public:
        float centerX;
        float centerY;
        float old_x;
        float old_y;
        float radius;
        Color color;
        Velocity v;
        float mass;

        Ball(float x, float y, float r, Color c, Velocity v, float m)
            : centerX(x), centerY(y), radius(r), color(c), v(v), mass(m) {;};
        Ball(float x, float y, float r) : centerX(x), centerY(y), radius(r) {;};
        Ball(){;}
        ~Ball() = default;
        Vector2 getCenter(){return {centerX, centerY};}
        void Move();
        void reMove();

};

#endif
