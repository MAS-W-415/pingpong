#include "raylib.h"
#include <cstdio>
#include "game.h"



int main (int argc, char *argv[]) {
    Game game;
    InitWindow(game.windowWidth, game.windowHeight, game.windowName.data());
    SetTargetFPS(game.FPS);
    
    while(!WindowShouldClose())
    {
        game.Init();
        int choise = game.StartPage();
        switch (choise)
        {
            case 1:
                game.Run();
                break;
            case 0:
                CloseWindow();
                break;
            default:;
        }

    }
    return 0;
}
