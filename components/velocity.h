#ifndef VELOCITY_H
#define VELOCITY_H

#include "Line.h"
#include <utility>

class Velocity
{
    public:
        inline static float MAX_Velocity = 500.0f;
        float vx = 0.0f;
        float vy = 0.0f;

        Velocity(float vx, float vy) : vx(vx), vy(vy){;}
        Velocity(){;}
        ~Velocity() = default;
        Velocity static ZERO(){return {};}

        void speedUp(float incrementX, float incrementY);
        void speedCut(float decrementX, float decrementY);
        static float projection(Velocity v, Line target);
        static Velocity change_basis2XY(float v_n, float v_t, Line normal);
        

};


#endif
