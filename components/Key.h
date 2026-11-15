#ifndef KEY_H
#define KEY_H

#include <raylib.h>
#include <utility>
class Key 
{
    public:
        float timer = 0.0f;
        float interval = 0.1f;
        KeyboardKey name;

        Key(){;}
        Key(float t, float interval, KeyboardKey key) 
            : timer(t), 
            interval(interval), 
            name(key) {;}
        Key(KeyboardKey key) : name(key) {;}

        template <typename T>
        void Press(T&& func)
        {
            if(IsKeyDown(this->name))
            {
                this->timer -= GetFrameTime();
                if(IsKeyPressed(this->name) || this->timer <= 0.0f)
                {
                    std::forward<T>(func)();
                    this->timer += this->interval;
                }
            }
            else 
            {
                this->timer = 0.0f;
            }
        }
            
        template <typename T>
        void NoPress(T&& func)
        {
            if(IsKeyUp(this->name))
            {
                std::forward<T>(func)();
            }
        }

        template <typename T>
        void doublePress(T&& func);

};

#endif 
