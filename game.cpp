#include "game.h"
#include <algorithm>
#include <cstdio>
#include <raylib.h>
#include <string>

void Game::Init()
{
    p_left = Paddle(
            Rectangle{
                (float)windowWidth / 10 - (float)windowWidth / 30,
                (float)windowHeight / 3, (float)windowWidth / 30,
                (float)windowHeight / 3},
            WHITE, 
            Velocity(0.0f, 0.0f));

    p_right = Paddle(
            Rectangle{
                windowWidth - (float)windowWidth / 10,
                (float)windowHeight / 3, 
                (float)windowWidth / 30,
                (float)windowHeight / 3},
            WHITE, 
            Velocity(0.0f, 0.0f));

    ball = Ball(
            (float)windowWidth / 2,
            (float)windowHeight / 2, 
            (float)windowWidth / 60,
            WHITE, 
            Velocity(Velocity::MAX_Velocity, 0.0f));

    upperBoundary = Line(
            0.0f,
            0.0f, 
            (float)windowWidth,
            0.0f,
            WHITE);

    bottomBoundary = Line(
            0.0f,
            (float)windowHeight, 
            (float)windowWidth,
            (float)windowHeight,
            WHITE);

    leftBoundary = Line(
            0.0f,
            0.0f,
            0.0f,
            (float)windowHeight, WHITE);

    rightBoundary = Line(
            (float)windowWidth,
            0.0f, 
            (float)windowWidth,
            (float)windowHeight, 
            WHITE);
};

void Game::Run()
{
    while(!isEnd)
    {
        if(IsKeyPressed(KEY_SPACE))
        {
            isPause = !isPause;
        }
        if(!isPause)
        {
            handleKeyboard();
            DoTheMove();
            handleCollision();
        }

        BeginDrawing();
            drawBackground();
            drawItems();
        EndDrawing();
    }
}

void Game::drawItems()
{
    DrawRectangleRec(p_right.rec, p_right.color);
    DrawRectangleRec(p_left.rec, p_left.color);

    DrawCircleLines(
            ball.centerX,
            ball.centerY,
            ball.radius,
            ball.color);

    DrawLine(upperBoundary.startPosX,
            upperBoundary.startPosY,
            upperBoundary.endPosX, 
            upperBoundary.endPosY, 
            upperBoundary.color);

    DrawLine(bottomBoundary.startPosX,
            bottomBoundary.startPosY, 
            bottomBoundary.endPosX,
            bottomBoundary.endPosY,
            bottomBoundary.color);

    DrawLine(leftBoundary.startPosX,
            leftBoundary.startPosY,
            leftBoundary.endPosX,
            leftBoundary.endPosY,
            leftBoundary.color);

    DrawLine(rightBoundary.startPosX,
            rightBoundary.startPosY,
            rightBoundary.endPosX,
            rightBoundary.endPosY,
            rightBoundary.color);
}

void Game::drawBackground()
{
    ClearBackground(BLACK);
}

void Game::handleKeyboard()
{

    if((IsKeyUp(KEY_UP) && IsKeyUp(KEY_DOWN)) || p_right.isSTOP > 0.0f)
    {
        p_right.v.speedCut(0.0f, d_acceleration * GetFrameTime());
    }

    if((IsKeyUp(KEY_W) && IsKeyUp(KEY_S)) || p_left.isSTOP > 0.0f)
    {
        p_left.v.speedCut(0.0f, d_acceleration * GetFrameTime());
    }

    if(IsKeyDown(KEY_UP) && p_right.isSTOP == 0.0f)
    {
        if(p_right.v.vy > 0.0f)
        {
            p_right.v.vy = p_right.v.vy * turnBackFactor;
            p_right.v.speedCut(0.0f, d_acceleration * GetFrameTime());
        }
        else if(p_right.v.vy == 0.0f)
        {
            p_right.v.vy -= 0.1f;
        }
        else 
        {
            p_right.v.speedUp(0.0f, acceleration * GetFrameTime());
        }
    }

    if(IsKeyDown(KEY_DOWN) && p_right.isSTOP == 0.0f)
    {
        if(p_right.v.vy < 0.0f)
        {
            p_right.v.vy = p_right.v.vy * turnBackFactor;
            p_right.v.speedCut(0.0f, d_acceleration * GetFrameTime());
        }
        else if(p_right.v.vy == 0.0f)
        {
            p_right.v.vy += 0.1f;
        }
        else 
        {
            p_right.v.speedUp(0.0f, acceleration * GetFrameTime());
        }
    }

    if(IsKeyDown(KEY_W) && p_left.isSTOP == 0.0f)
    {
        if(p_left.v.vy > 0.0f)
        {
            p_left.v.vy = p_left.v.vy * turnBackFactor;
            p_left.v.speedCut(0.0f, d_acceleration * GetFrameTime());
        }
        else if(p_left.v.vy == 0.0f)
        {
            p_left.v.vy -= 0.1f;
        }
        else
        {
            p_left.v.speedUp(0.0f, acceleration * GetFrameTime());
        }
    }

    if(IsKeyDown(KEY_S) && p_left.isSTOP == 0.0f)
    {
        if(p_left.v.vy < 0.0f)
        {
            p_left.v.vy = p_left.v.vy * turnBackFactor;
            p_left.v.speedCut(0.0f, d_acceleration * GetFrameTime());
        }
        else if(p_left.v.vy == 0.0f)
        {
            p_left.v.vy += 0.1f;
        }
        else
        {
            p_left.v.speedUp(0.0f, acceleration * GetFrameTime());
        }
    }
}

void Game::handleCollision()
{
    if(
        CheckCollisionCircleRec(
            {ball.centerX, ball.centerY},
            ball.radius,
            p_right.rec)
    )
    {
        ball.v.vx = -ball.v.vx;
        ball.v.speedUp(0.0f, p_right.v.vy * collisionFactor);
    }

    if(
        CheckCollisionCircleRec(
            {ball.centerX, ball.centerY},
            ball.radius,
            p_left.rec)
    )
    {
        ball.v.vx = -ball.v.vx;
        ball.v.speedUp(0.0f, p_left.v.vy * collisionFactor);
    }

    if(
        CheckCollisionCircleLine(
            {ball.centerX, ball.centerY},
            ball.radius,
            {upperBoundary.startPosX, upperBoundary.startPosY},
            {upperBoundary.endPosX, upperBoundary.endPosY})
        ||
        CheckCollisionCircleLine(
            {ball.centerX, ball.centerY},
            ball.radius,
            {bottomBoundary.startPosX, bottomBoundary.startPosY}, 
            {bottomBoundary.endPosX, bottomBoundary.endPosY})
    )
    {
        ball.v.vy = -ball.v.vy;
    }

    if(
        CheckCollisionLines(
            {p_left.rec.x, p_left.rec.y}, 
            {p_left.rec.x, p_left.rec.y + p_left.rec.height}, 
            {upperBoundary.startPosX, upperBoundary.startPosY},
            {upperBoundary.endPosX, upperBoundary.endPosY},
            NULL) 
        || 
        CheckCollisionLines(
            {p_left.rec.x, p_left.rec.y}, 
            {p_left.rec.x, p_left.rec.y + p_left.rec.height}, 
            {bottomBoundary.startPosX, bottomBoundary.startPosY},
            {bottomBoundary.endPosX, bottomBoundary.endPosY}, 
            NULL)
    )
    {
        if(p_left.rec.y < 0.0f)
        {
            p_left.rec.y = 1.0f;
        }
        if(p_left.rec.y > windowHeight - p_left.rec.height)
        {
            p_left.rec.y = windowHeight - p_left.rec.height - 1.0f;
        }
        p_left.v.vy = -p_left.v.vy;
        Stop(&p_left.isSTOP, 0.2f);
    }

    if(
        CheckCollisionCircleLine(
            {ball.centerX, ball.centerY}, 
            ball.radius, 
            {leftBoundary.startPosX, leftBoundary.startPosY},
            {leftBoundary.endPosX, leftBoundary.endPosY}) 
        || 
        CheckCollisionCircleLine(
            {ball.centerX, ball.centerY}, 
            ball.radius, 
            {rightBoundary.startPosX, rightBoundary.startPosY},
            {rightBoundary.endPosX, rightBoundary.endPosY})
    )
    {
        isEnd = true;
    }

    if(
        CheckCollisionLines(
            {p_right.rec.x, p_right.rec.y}, 
            {p_right.rec.x, p_right.rec.y + p_right.rec.height}, 
            {upperBoundary.startPosX, upperBoundary.startPosY},
            {upperBoundary.endPosX, upperBoundary.endPosY},
            NULL) 
        || 
        CheckCollisionLines(
            {p_right.rec.x, p_right.rec.y}, 
            {p_right.rec.x, p_right.rec.y + p_right.rec.height}, 
            {bottomBoundary.startPosX, bottomBoundary.startPosY},
            {bottomBoundary.endPosX, bottomBoundary.endPosY},
            NULL)
    )
    {
        if(p_right.rec.y < 0.0f)
        {
            p_right.rec.y = 1.0f;
        }
        if(p_right.rec.y > windowHeight - p_right.rec.height)
        {
            p_right.rec.y = windowHeight - p_right.rec.height - 1.0f;
        }
        p_right.v.vy = -p_right.v.vy;
        Stop(&p_right.isSTOP, 0.2f);
    }
}

void Game::DoTheMove()
{
    p_right.rec.y += p_right.v.vy * GetFrameTime();
    p_left.rec.y += p_left.v.vy * GetFrameTime();
    ball.centerX += ball.v.vx * GetFrameTime();
    ball.centerY += ball.v.vy * GetFrameTime();
    p_right.isSTOP = std::max(p_right.isSTOP - GetFrameTime(), 0.0f);
    p_left.isSTOP = std::max(p_left.isSTOP - GetFrameTime(), 0.0f);
}

void Game::Stop(float* target, float time)
{
    (*target) += time;
}

int Game::StartPage()
{
    while(true)
    {
        if(IsKeyPressed(KEY_G))
        {
            return 1;
        }
        if(IsKeyPressed(KEY_ESCAPE))
        {
            return 0;
        }
        BeginDrawing();
            drawBackground();
            int w = MeasureText(windowName.data(), 50);
            DrawText(
                    windowName.data(), 
                    (windowWidth - w) / 2, 
                    windowHeight / 3, 
                    50,
                    WHITE);
        EndDrawing();

    }
}
