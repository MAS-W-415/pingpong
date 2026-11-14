#ifndef COLLISION_H
#define COLLISION_H

#include "./ball.h"
#include "./paddle.h"
#include "./Line.h"
#include "raylib.h"

class Collision
{
    public:
        inline static float sleep_time = 0.5f;
        //  recovery_coefficient恢复系数（轴向、切向）
        inline static float e_normal= 1.0f;
        inline static float e_tangent= 1.0f;
        static void ball_with_paddle(Ball& ball, Paddle& paddle);
        static void ball_with_line(Ball& ball, Line& line);
        static void ball_with_endLine(Ball ball, Line line, bool& key);
        static void paddle_with_line(Paddle& paddle, Line& line);

    private:
        static void Basic_Two_Obj(const float& m1, Velocity& v1, 
                const float& m2, Velocity& v2,
                Line normal);

};


#endif
