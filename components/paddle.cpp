#include "paddle.h"
#include "raylib.h"
#include <string>

Vector2 Paddle::getCenter()
{
    return Vector2{
            this->rec.x + this->rec.width / 2, 
            this->rec.y + this->rec.height / 2};
}

Line Paddle::getBoundaryLine(const std::string direction)
{
    if(direction == "left")
    {
        return Line(this->rec.x, this->rec.y, 
                this->rec.x, this->rec.y + this->rec.height);
    }
    else if(direction == "upper")
    {
        return Line(this->rec.x, this->rec.y,
                this->rec.x + this->rec.width, this->rec.y);
    }
    else if(direction == "right")
    {
        return Line(this->rec.x + this->rec.width, this->rec.y,
                this->rec.x + this->rec.width, this->rec.y + this->rec.height);
    }
    else if(direction == "bottom")
    {
        return Line(this->rec.x, this->rec.y + this->rec.height,
                this->rec.x + this->rec.width, this->rec.y + this->rec.height);
    }
    else{return Line();}
}

void Paddle::Move()
{
    if(this->isNeedRemove)
    {
        this->isNeedRemove = false;
        this->reMove();
        return;
    }
    this->old_rec = this->rec;
    //    this->rec.x += this->v.vx * GetFrameTime();
    this->rec.y += this->v.vy * GetFrameTime();
}

void Paddle::reMove()
{
    this->rec = this->old_rec;
}

void Paddle::goUP()
{
    if(this->v.vy > 0.0f)
    {
        this->v.vy = this->v.vy * turnBackFactor;
        this->v.speedCut(0.0f, this->d_acc * GetFrameTime());
    }
    else if(this->v.vy == 0.0f)
    {
        this->v.vy -= 0.1f;
    }
    else 
    {
        this->v.speedUp(0.0f, this->acc * GetFrameTime());
    }
}

void Paddle::slowDown()
{
    this->v.speedCut(0.0f, this->d_acc * GetFrameTime());
}

void Paddle::goDown()
{
    if(this->v.vy < 0.0f)
    {
        this->v.vy = this->v.vy * turnBackFactor;
        this->v.speedCut(0.0f, this->d_acc * GetFrameTime());
    }
    else if(this->v.vy == 0.0f)
    {
        this->v.vy += 0.1f;
    }
    else 
    {
        this->v.speedUp(0.0f, this->acc * GetFrameTime());
    }
}
