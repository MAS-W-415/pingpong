# Pingpong

Small C++17/raylib 5.5 Pong demo. Public repo: https://github.com/MAS-W-415/pingpong. There are no tests; see `README.md` for controls and setup.

## Build and run
- `make` builds `./pingpong` from all `*.cpp` files in the root and `components/`.
- `make run` builds and launches the game; requires a graphical display.
- `make clean` removes `./pingpong`.
- Requires `g++`, `make`, and system raylib 5.5 (`pkg-config --modversion raylib`).

## Layout
- `main.cpp` is the entrypoint: creates `Game`, opens the raylib window, and runs the outer loop.
- `game.cpp` / `game.h`: `Game` owns the paddles, ball, boundaries, input, collision handling, and rendering.
- `components/`: `Paddle`, `Ball`, and `Line` are header-only; `Velocity` is implemented in `velocity.cpp`.
- New `.cpp` files are picked up automatically by the Makefile.

## Traps
- Files ending in `~` are editor backups; ignore them.
