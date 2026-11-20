#include "paddle.h"
#include "raylib.h"
#include <string>

Vector2 Paddle::getCenter() 
{
    return Vector2{
            form.rec.x + form.rec.width / 2, 
            form.rec.y + form.rec.height / 2};
}

void Paddle::move_p() 
{
    //  form.rec.x += v.vx * GetFrameTime();
    form.rec.y += v.vy * GetFrameTime();
}

Rectangle Paddle::getRec() 
{
    return form.rec; 
}

Line Paddle::getBoundaryLine(const std::string direction)
{
    if(direction == "left")
    {
        return Line(form.rec.x, form.rec.y, 
                form.rec.x, form.rec.y + form.rec.height);
    }
    else if(direction == "upper")
    {
        return Line(form.rec.x, form.rec.y,
                form.rec.x + form.rec.width, form.rec.y);
    }
    else if(direction == "right")
    {
        return Line(form.rec.x + form.rec.width, form.rec.y,
                form.rec.x + form.rec.width, form.rec.y + form.rec.height);
    }
    else if(direction == "bottom")
    {
        return Line(form.rec.x, form.rec.y + form.rec.height,
                form.rec.x + form.rec.width, form.rec.y + form.rec.height);
    }
    else{return Line();}
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

