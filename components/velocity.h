#ifndef VELOCITY_H
#define VELOCITY_H


class Velocity
{
    public:
        static constexpr float MAX_Velocity = 500.0f;
        float vx = 0.0f;
        float vy = 0.0f;

        Velocity(float vx, float vy) : vx(vx), vy(vy){;}
        Velocity(){;}
        ~Velocity() = default;

        void speedUp(float incrementX, float incrementY);
        void speedCut(float decrementX, float decrementY);

};

#endif
