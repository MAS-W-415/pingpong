# Pingpong

English | [简体中文](README.zh-CN.md)

A small two-player Pong demo built with C++17 and [raylib](https://www.raylib.com/).

## Overview

Pingpong includes two paddles, a bouncing ball, boundary collisions, collision sound effects, pause support, and a start screen. A round ends when the ball crosses the left or right boundary.

## Controls

| Input | Action |
| --- | --- |
| `W` / `S` | Move left paddle up / down |
| `Up` / `Down` | Move right paddle up / down |
| `Space` | Start the game from the start screen; pause / resume during a round |
| `Esc` / close window | Quit from the start screen |

## Requirements

- A C++17 compiler (`g++`)
- `make`
- raylib 5.5 development files with `pkg-config` metadata
- A graphical display

## Build and run

```bash
make
make run
```

`make` builds `./pingpong`; `make clean` removes it. Verify the raylib version with:

```bash
pkg-config --modversion raylib
```

Run the game from the repository root so the relative paths under `sounds/` resolve correctly.

## Project structure

```text
main.cpp              Entrypoint and window loop
game.cpp / game.h     Game state, input, collisions, rendering
components/           Paddle, Ball, Line, Velocity
sounds/               WAV sound effects
Makefile              Build and run targets
```

## License

MIT
