#include "Line.h"

Line Line::get_vertical_line(Line l)
{
    return Line(l.startPosX, 
            l.startPosY, 
            l.startPosX - l.endPosY + l.startPosY, 
            l.startPosY + l.endPosX - l.startPosX);
}

Vector2 Line::get_pedal_point(Line l, Vector2 point)
{
    float dx = l.endPosX - l.startPosX;
    float dy = l.endPosY - l.startPosY;
    float t = ((point.x - l.startPosX) * dx + (point.y - l.startPosY) * dy) / (dx * dx + dy * dy);
    return {l.startPosX + t * dx, l.startPosY + t * dy};
}
