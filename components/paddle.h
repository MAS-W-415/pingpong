#ifndef PADDLE_H
#define PADDLE_H

#include "raylib.h"
#include "velocity.h"
#include <string>

class Paddle
{
    public:
        Rectangle rec;
        Rectangle old_rec;
        Color color;
        Velocity v;
        float mass;

        Paddle(Rectangle rec, Color c, Velocity v, float m) 
            : rec(rec), color(c), v(v), mass(m){;};
        Paddle(){;}
        ~Paddle() = default;
        Vector2 getCenter();
        //  right \ upper \ left \ bottom
        Line getBoundaryLine(const std::string direction);
        void Move();
        void reMove();

};

#endif
