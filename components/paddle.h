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
        inline static float acc = 10000.0f;
        inline static float d_acc = 1000.0f;
        inline static float turnBackFactor = 0.5f;

        bool isNeedRemove = false;

        Paddle(Rectangle rec, Color c, Velocity v, float m) 
            : rec(rec), color(c), v(v), mass(m){;};
        Paddle(){;}
        ~Paddle() = default;
        Vector2 getCenter();
        //  right \ upper \ left \ bottom
        Line getBoundaryLine(const std::string direction);
        void Move();
        void goUP();
        void goDown();
        void slowDown();

    private:
        void reMove();

};

#endif
