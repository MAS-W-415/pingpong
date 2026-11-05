#include "raylib.h"
#include <cstdio>
#include "game.h"



int main (int argc, char *argv[]) {
    Game game;
    game.BasicSet();


    while(!WindowShouldClose())
    {
        game.Init();
        switch (game.StartPage())
        {
            case 1:
                game.Run();
                break;
            case 0:
                game.endGame();
                break;
            default:;
        }

    }
    return 0;
}
