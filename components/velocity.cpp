#include "velocity.h"
#include <algorithm>

void Velocity::speedUp(float incrementX, float incrementY)
{
    if(this->vx > 0.0f)
    {
        this->vx = std::min(this->vx + incrementX, MAX_Velocity);
    }
    else
    {
        this->vx = std::max(this->vx - incrementX, -MAX_Velocity);
    }

    if(this->vy > 0.0f)
    {
        this->vy = std::min(this->vy + incrementY, MAX_Velocity);
    }
    else
    {
        this->vy = std::max(this->vy - incrementY, -MAX_Velocity);
    }
}

void Velocity::speedCut(float decrementX, float decrementY)
{
    if(this->vx > 0.0f)
    {
        this->vx = std::max(this->vx - decrementX, 0.0f);
    }
    else
    {
        this->vx = std::min(this->vx + decrementX, 0.0f);
    }

    if(this->vy > 0.0f)
    {
        this->vy = std::max(this->vy - decrementY, 0.0f);
    }
    else
    {
        this->vy = std::min(this->vy + decrementY, 0.0f);
    }
}
