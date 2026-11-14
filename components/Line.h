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
        inline static float mass = 1.0e9f;

        Line(float spx, float spy, float epx, float epy, Color c)
            : startPosX(spx), startPosY(spy), endPosX(epx), endPosY(epy), color(c) {;}
        Line(float spx, float spy, float epx, float epy) 
            : startPosX(spx), startPosY(spy), endPosX(epx), endPosY(epy) {;}
        Line(Vector2 startPos, Vector2 endPos)
            : startPosX(startPos.x), startPosY(startPos.y), 
            endPosX(endPos.x), endPosY(endPos.y) {;}
        Line(){;}
        ~Line() = default;
        Vector2 getStartPos(){return {startPosX, startPosY};}
        Vector2 getEndPos(){return {endPosX, endPosY};}


        static Line get_vertical_line(Line l);
        static Vector2 get_pedal_point(Line l, Vector2 point);
};

#endif 
