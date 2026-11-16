#include "./ball.h"
#include "raylib.h"

void Ball::Move()
{
    if(this->isNeedRemove)
    {
        this->isNeedRemove = false;
        Ball::reMove();
        return;
    }
    this->old_x = this->centerX;
    this->old_y = this->centerY;
    this->centerX += this->v.vx * GetFrameTime();
    this->centerY += this->v.vy * GetFrameTime();
}

void Ball::reMove()
{
    this->centerX = this->old_x;
    this->centerY = this->old_y;
}
