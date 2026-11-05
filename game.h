#ifndef GAME_H
#define GAME_H

#include <cstdint>
#include <ctime>
#include <string>
#include <string_view>
#include "raylib.h"
#include "./components/paddle.h"
#include "./components/velocity.h"
#include "./components/ball.h"
#include "./components/Line.h"

#define START_GAME true
#define EXIT_GAME false


class Game 
{
    public:
        static constexpr int FPS = 60;
        static constexpr int windowWidth = 800;
        static constexpr int windowHeight = 600;
        static constexpr std::string_view windowName = "Ping Pong";

    private:
        bool isPause = false;
        bool isEnd = false;

        static constexpr int NameSize = 100;
        static constexpr int HintSize = 20;
        static constexpr std::string_view startHint_1 = "press space to start game";
        static constexpr std::string_view startHint_2 = "press ECS to exit game";
        inline static Sound sound_collision;

        float acceleration = 1000.0f;
        float d_acceleration = 1000.0f;
        float turnBackFactor = 0.5f;
        float collisionFactor = 0.5f;

        Paddle p_left; 
        Paddle p_right;
        Ball ball;
        Line upperBoundary;
        Line bottomBoundary;
        Line leftBoundary;
        Line rightBoundary;

    public:
        Game(){;}
        ~Game() = default; 
        void BasicSet();
        void Init();
        void Run();
        int StartPage();
        void endGame();

    private:
        void drawItems();
        void drawBackground();
        void drawStartPage();
        void handleKeyboard();
        void handleCollision();
        void DoTheMove();
        //  time for seconds
        void Stop(float* target, float time);

        void UnloadAnySound();
        void loadEverySound();




};

#endif

