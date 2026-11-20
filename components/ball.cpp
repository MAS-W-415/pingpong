#include "./ball.h"
#include "raylib.h"

void Ball::move_p()
{
    form.pos.x += v.vx * GetFrameTime();
    form.pos.y += v.vy * GetFrameTime();
}

Rectangle Ball::getRec()
{
    return Rectangle{form.pos.x - form.radius, form.pos.y - form.radius, form.radius * 2.0f, form.radius * 2.0f};
}

void Ball::multiCollision()
{
    asset = {"ball.pop", assetMap.at("ball.pop")};
}
