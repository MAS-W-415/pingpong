#ifndef SOUND_H
#define SOUND_H

#include "raylib.h"

class SOUND 
{
    public:
        inline static Sound colli_ball2rec;
        inline static Sound colli_rec2wall;
        inline static Sound colli_ballOut;
        
        void static init()
        {
            InitAudioDevice();
            colli_ball2rec = LoadSound("sounds/bounce.wav");
            colli_rec2wall = LoadSound("sounds/paddle2wall.wav");
            colli_ballOut = LoadSound("sounds/pop.wav");
        }

        void static unload()
        {
            UnloadSound(colli_ball2rec);
            UnloadSound(colli_rec2wall);
            UnloadSound(colli_ballOut);
        }
        

};

#endif 
