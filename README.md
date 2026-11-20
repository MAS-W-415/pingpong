# Pingpong

English | [简体中文](README.zh-CN.md)

A small two-player Pong demo built with C++17 and [raylib](https://www.raylib.com/) 5.5.

## Overview

Pingpong includes two paddles, a bouncing ball, boundary collisions, collision
sound effects, and a start screen. The game uses one combined sprite asset:
a dreamy sky background, a bubble ball, cloud paddles, trail frames, and a
bubble-pop animation.

## Controls

| Input | Action |
| --- | --- |
| `W` / `S` | Move left paddle up / down |
| `Up` / `Down` | Move right paddle up / down |
| `Space` | Start the game from the start screen |
| `Esc` / close window | Quit |

## Requirements

- A C++17 compiler (GCC or Clang; the Makefile force-includes the local `raylib.h` overlay)
- `make`
- raylib 5.5 development files with `pkg-config` metadata
- A graphical display

## Build and run

```bash
make
make run
```

`make` builds `./pingpong`; `make clean` removes it. New `.cpp` files in the
repository root or `components/` are picked up automatically.

Verify the raylib version with:

```bash
pkg-config --modversion raylib
```

Run the game from the repository root so the relative paths under `assets/`
and `sounds/` resolve correctly.

## Project structure

```text
main.cpp                  Entrypoint and window loop
game.cpp / game.h         Game state, input, collisions, rendering, state flow
components/               Entities, collision, input, asset loading, sound helpers
assets/pingpong-art/      Combined sprite sheet, manifest, build script, art docs
assets/pingpong-art.tar.gz
sounds/                   WAV sound effects
raylib.h                  Local raylib overlay header
Makefile                  Build and run targets
```

The combined art asset is documented in
[`assets/pingpong-art/README.md`](assets/pingpong-art/README.md). Its
`pingpong-art.spritepos` manifest uses whitespace-delimited `[meta]`,
`[frames]`, and `[animations]` sections; `build.py` regenerates the PNG and
manifest together.

Current sound effects:

- `sounds/bounce.wav`
- `sounds/paddle2wall.wav`
- `sounds/pop.wav`

## Release

[v1.0.0](https://github.com/MAS-W-415/pingpong/releases/tag/v1.0.0)

No prebuilt binaries or downloadable build artifacts are provided; build from
source with `make`.

## License

The source code is MIT licensed. The combined art pack under
`assets/pingpong-art/` is released under CC0-1.0; see its `LICENSE` file.
