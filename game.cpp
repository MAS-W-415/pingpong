#include "game.h"
#include <algorithm>
#include <cmath>
#include <cstdio>
#include "components/sound.h"
#include "raylib.h"
#include <functional>
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
            handleCollision();
            DoTheMove();
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
    if(IsKeyUp(UP.name) && IsKeyUp(DOWN.name))
    {
        p_right.slowDown();
    }

    if(IsKeyUp(W.name) && IsKeyUp(S.name))
    {
        p_left.slowDown();
    }

    UP.Press([this]()
            {
                p_right.goUP();
            });

    DOWN.Press([this]()
            {
                p_right.goDown();
            });

    W.Press([this]()
            {
                p_left.goUP();
            });

    S.Press([this]()
            {
                p_left.goDown();
            });
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
    SOUND::unload();
    CloseAudioDevice();
    CloseWindow();
}


void Game::BasicSet()
{
    SetConfigFlags(FLAG_WINDOW_RESIZABLE | FLAG_VSYNC_HINT);
    InitWindow(windowWidth, windowHeight, windowName.data());
    SOUND::init();
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
