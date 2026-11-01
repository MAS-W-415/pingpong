#ifndef PADDLE_H
#define PADDLE_H

#include "raylib.h"
#include "velocity.h"

class Paddle
{
    public:
        Rectangle rec;
        Color color;
        Velocity v;
        float isSTOP = 0.0f;

        Paddle(Rectangle rec, Color c, Velocity v) : rec(rec), color(c), v(v) {;};
        Paddle(){;}
        ~Paddle() = default;

};

#endif
