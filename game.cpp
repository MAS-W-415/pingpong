#include "game.h"
#include <algorithm>
#include <cmath>
#include <cstdio>
#include "raylib.h"
#include <raylib.h>
#include <string>
#include <string_view>

void Game::Init()
{
    isEnd = false;

    p_left = Paddle(
            Rectangle{
                (float)windowWidth / 10 - (float)windowWidth / 30,
                (float)windowHeight / 3, (float)windowWidth / 30,
                (float)windowHeight / 3},
            WHITE, 
            Velocity(0.0f, 0.0f),
            100.0f);

    p_right = Paddle(
            Rectangle{
                windowWidth - (float)windowWidth / 10,
                (float)windowHeight / 3, 
                (float)windowWidth / 30,
                (float)windowHeight / 3},
            WHITE, 
            Velocity(0.0f, 0.0f),
            100.0f);

    ball = Ball(
            (float)windowWidth / 2,
            (float)windowHeight / 2, 
            (float)windowWidth / 60,
            WHITE, 
            Velocity(Velocity::MAX_Velocity, 0.0f),
            1.0f);

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
    isPause = true;
    while(!isEnd && !(isPause && IsKeyPressed(KEY_ESCAPE)))
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

    if((IsKeyUp(KEY_UP) && IsKeyUp(KEY_DOWN)))
    {
        p_right.v.speedCut(0.0f, d_acceleration * GetFrameTime());
    }

    if((IsKeyUp(KEY_W) && IsKeyUp(KEY_S)))
    {
        p_left.v.speedCut(0.0f, d_acceleration * GetFrameTime());
    }

    if(IsKeyDown(KEY_UP))
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

    if(IsKeyDown(KEY_DOWN))
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

    if(IsKeyDown(KEY_W))
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

    if(IsKeyDown(KEY_S))
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

    Collision::ball_with_paddle(ball, p_left);
    Collision::ball_with_paddle(ball, p_right);
    Collision::ball_with_line(ball, upperBoundary);
    Collision::ball_with_line(ball, bottomBoundary);
    Collision::ball_with_endLine(ball, leftBoundary, isEnd);
    Collision::ball_with_endLine(ball, rightBoundary, isEnd);
    Collision::paddle_with_line(p_left, upperBoundary);
    Collision::paddle_with_line(p_left, bottomBoundary);
    Collision::paddle_with_line(p_right, upperBoundary);
    Collision::paddle_with_line(p_right, bottomBoundary);

}

void Game::DoTheMove()
{
    p_right.Move();
    p_left.Move();
    ball.Move();
}

void Game::Stop(float* target, float time)
{
    (*target) += time;
}

int Game::StartPage()
{
    while(true)
    {
        if(IsKeyPressed(KEY_SPACE))
        {
            return START_GAME;
        }
        if(WindowShouldClose())
        {
            return EXIT_GAME;
        }
        BeginDrawing();
            drawStartPage();
        EndDrawing();

    }
}

void Game::drawStartPage()
{
    drawBackground();
    int name_width = MeasureText(windowName.data(), NameSize);
    DrawText(
            windowName.data(), 
            (windowWidth - name_width) / 2, 
            windowHeight / 3, 
            NameSize,
            WHITE
            );
    
    static int hint_index= 0;
    if(drawHint(hints[hint_index]) == 0) 
    {
        hint_index = GetRandomValue(0, Game::HintNum - 1);
    }
}

void Game::endGame()
{
    UnloadAnySound();
    CloseAudioDevice();
    CloseWindow();
}

void Game::UnloadAnySound()
{
    UnloadSound(Game::sound_collision_ball2rec);
    UnloadSound(Game::sound_collision_rec2wall);
    UnloadSound(Game::sound_ball_out);
}

void Game::BasicSet()
{
    SetConfigFlags(FLAG_WINDOW_RESIZABLE | FLAG_VSYNC_HINT);
    InitWindow(windowWidth, windowHeight, windowName.data());
    InitAudioDevice();
    Game::sound_collision_ball2rec = LoadSound("./sounds/random.wav");
    Game::sound_collision_rec2wall = LoadSound("./sounds/explosion.wav");
    Game::sound_ball_out = LoadSound("./sounds/random (1).wav");
}

bool Game::drawHint(const std::string_view& hint)
{
    double time = GetTime();
    double alpha = std::max(std::sin(time), 0.0);
    int hint_width = MeasureText(hint.data(), HintSize);
    DrawText(
            hint.data(), 
            (windowWidth - hint_width) / 2, 
            2 * windowHeight / 3, 
            HintSize,
            Fade(WHITE, alpha)
            );
    return alpha != 0.0;
}
