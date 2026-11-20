#ifndef OBJECT_H
#define OBJECT_H

#include "raylib.h"
#include "./velocity.h"
#include <algorithm>
#include <string>
#include <utility>
#include <vector>
#include "Assets.h"



template <typename T>
class Object 
{
    public:
        T form{};
        T old_form{};
        Color color;
        Velocity v;
        float mass;
        bool isNeedRemove = false;
        bool pre_state = false;
        std::pair<std::string, _Asset> asset;
        std::pair<std::string, _Asset> old_asset;

        Object() = default;
        explicit Object(T f) : form(std::move(f)), old_form(std::move(f)) {;}
        explicit Object(T f, Color c, Velocity v, float m,
                const std::string& n, const _Asset& a) :
            form(std::move(f)), old_form(std::move(f)), color(c), 
            v(v), mass(m), asset{n, a} {;}
    
    //  below is for draw asset 
    protected:
        float timer = 0.0f;
        int index = 0;
        int len_pos = 0;
        std::string asset_name = "";

    public:
        virtual Vector2 getCenter() = 0;
        void drawAsset(Texture& tex);
        void Move();

    protected:
        void reMove();
        virtual void move_p() = 0;
        virtual Rectangle getRec() = 0;

};


struct REC 
{
    Rectangle rec = {};
};

struct CIRCLE 
{
    Vector2 pos = {};
    float radius = 0.0f;
};

#endif 
