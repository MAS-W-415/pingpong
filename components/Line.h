#ifndef LINE_H
#define LINE_H

#include "raylib.h"

class Line 
{
    public:
        float startPosX;
        float startPosY;
        float endPosX;
        float endPosY;
        Color color;

        Line(float spx, float spy, float epx, float epy, Color c) : startPosX(spx), startPosY(spy), endPosX(epx), endPosY(epy), color(c) {;}
        Line(){;}
        ~Line() = default;
};

#endif 
