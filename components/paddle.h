#ifndef PADDLE_H
#define PADDLE_H

#include "raylib.h"
#include "velocity.h"
#include "Object.h" 
#include <string>
#include <vector>

class Paddle : public Object<REC> 
{
    public:
        Paddle(Rectangle r, Color c, Velocity v, float m, const std::string& asset_name, const _Asset& asset) : 
            Object(REC{r}, c, v, m, asset_name, asset) {;}
        Paddle()= default;
        ~Paddle() = default;
        Vector2 getCenter() override;

    private:
        void move_p() override;
        Rectangle getRec() override;
    

    public:
        //  right \ upper \ left \ bottom
        Line getBoundaryLine(const std::string direction);
        void goUP();
        void goDown();
        void slowDown();

    private:
        inline static float acc = 10000.0f;
        inline static float d_acc = 1000.0f;
        inline static float turnBackFactor = 0.5f;

};

#endif
