#ifndef BALL_H 
#define BALL_H



#include "raylib.h"
#include "velocity.h"
#include "Object.h" 
#include <optional>
#include <vector>

class Ball : public Object<CIRCLE>
{
    public:
        Ball(float x, float y, float r, Color c, Velocity v, float m,
                const std::string& name, const _Asset& asset) :
            Object<CIRCLE>(CIRCLE{x, y ,r}, c, v, m, name, asset) {;}
        Ball(float x, float y, float r) : Object<CIRCLE>(CIRCLE{x, y, r}) {;};
        Ball(){;}
        ~Ball() = default;
        Vector2 getCenter() override {return {form.pos.x, form.pos.y};}
        void multiCollision();

    private:
        void move_p() override;
        Rectangle getRec() override;


};

#endif
