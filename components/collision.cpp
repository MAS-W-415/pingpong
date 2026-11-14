#include "./collision.h"
#include "Line.h"
#include <algorithm>
#include "raylib.h"

void Collision::ball_with_endLine(Ball ball, Line line, bool& key)
{
    //  check
    if(CheckCollisionCircleLine(
                ball.getCenter(),
                ball.radius,
                line.getStartPos(),
                line.getEndPos())
      )
    {
        key = true;
    }
}

void Collision::paddle_with_line(Paddle& paddle, Line& line)
{
    Vector2 collision_point;
    if(MyCheckCollisionRecLine(
                paddle.rec, 
                line.getStartPos(),
                line.getEndPos(),
                collision_point)
      )
    {

        Line normal = Line(collision_point, paddle.getCenter());
        Velocity zero_v = Velocity::ZERO();
        Collision::Basic_Two_Obj(paddle.mass, paddle.v, line.mass, zero_v, normal);
        //  pos 
        paddle.reMove();
        return;
    }
}

void Collision::ball_with_line(Ball& ball, Line& line)
{
    //  check
    if(CheckCollisionCircleLine(
                ball.getCenter(),
                ball.radius,
                line.getStartPos(),
                line.getEndPos())
            )
    {
        //  velocity 
        float closestX = std::clamp(
            ball.centerX,
            line.startPosX,
            line.endPosX);
        float closestY = std::clamp(
            ball.centerY,
            line.startPosY,
            line.endPosY);
        Vector2 collision_point = {closestX, closestY}; 
        Line normal = Line(collision_point, ball.getCenter());
        Velocity zero_v = Velocity::ZERO();
        Collision::Basic_Two_Obj(ball.mass, ball.v, line.mass, zero_v, normal);
        //  pos 
        ball.reMove();
        return;
    }
}

void Collision::ball_with_paddle(Ball& ball, Paddle& paddle)
{
    //  check
    if(CheckCollisionCircleRec(
                ball.getCenter(),
                ball.radius,
                paddle.rec)
            )
    {
        //  velocity 
        float closestX = std::clamp(
            ball.centerX,
            paddle.rec.x,
            paddle.rec.x + paddle.rec.width);
        float closestY = std::clamp(
            ball.centerY,
            paddle.rec.y,
            paddle.rec.y + paddle.rec.height);
        Vector2 collision_point = {closestX, closestY}; 
        Line normal = Line(collision_point, ball.getCenter());
        Collision::Basic_Two_Obj(ball.mass, ball.v, paddle.mass, paddle.v, normal);
        //  pos 
        ball.reMove();
        paddle.reMove();
        return;
    }
}


void Collision::Basic_Two_Obj(
        const float& m1, Velocity& v1,
        const float& m2, Velocity& v2,
        Line normal)
{
    Line tangent = Line::get_vertical_line(normal);

    float v_1_normal = Velocity::projection(v1, normal);
    float v_1_tangent = Velocity::projection(v1, tangent);
    float v_2_normal = Velocity::projection(v2, normal);
    float v_2_tangent = Velocity::projection(v2, tangent);

    float v_1_normal_p = 
        ((m1 - Collision::e_normal * m2) * v_1_normal
        + m2 * (1 + Collision::e_normal) * v_2_normal)
         / (m1 + m2);

    float v_2_normal_p = 
        (m1 * (1 + Collision::e_normal) * v_1_normal 
        + (m2 - Collision::e_normal * m1) * v_2_normal)
        / (m1 + m2);

    float v_1_tangent_p = 
        ((m1 - Collision::e_tangent * m2) * v_1_tangent
         + m2 * (1 + Collision::e_tangent) * v_2_tangent)
        / (m1 + m2);

    float v_2_tangent_p = 
        ((m1 * (1 + Collision::e_tangent) * v_1_tangent)
         + (m2 - Collision::e_tangent * m1) * v_2_tangent)
        / (m1 + m2);

    v1 = Velocity::change_basis2XY(v_1_normal_p, v_1_tangent_p, normal);
    v2 = Velocity::change_basis2XY(v_2_normal_p, v_2_tangent_p, normal);
}
