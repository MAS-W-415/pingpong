#include "velocity.h"
#include <algorithm>
#include <cmath>

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

float Velocity::projection(Velocity v, Line target)
{
    float dx = target.endPosX - target.startPosX;
    float dy = target.endPosY - target.startPosY;
    float L = sqrtf(dx * dx + dy * dy);
    return (v.vx * dx + v.vy * dy) / L;
}

Velocity Velocity::change_basis2XY(float v_n, float v_t, Line normal)
{
    float dnx = normal.endPosX - normal.startPosX;
    float dny = normal.endPosY - normal.startPosY;
    float Ln = sqrtf(dnx * dnx + dny * dny);
    return {(v_t * dny + v_n * dnx) / Ln, (-v_t * dnx + v_n * dny) / Ln};
}
