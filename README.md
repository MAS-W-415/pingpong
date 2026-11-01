# Pingpong

A small Pong demo built with C++17 and [raylib](https://www.raylib.com/).

## 中文

### 简介

一个使用 C++17 和 raylib 5.5 编写的双人 Pong demo，包含左右球拍、球的反弹、边界碰撞、暂停功能和开始界面。球越过左边界或右边界时本局结束。

### 操作

| 按键 | 功能 |
| --- | --- |
| `W` / `S` | 左球拍上移 / 下移 |
| `↑` / `↓` | 右球拍上移 / 下移 |
| `Space` | 暂停 / 继续 |
| `G` | 在开始界面开始游戏 |
| `Esc` | 在开始界面退出 |

### 构建与运行

依赖：

- C++17 编译器（`g++`）
- `make`
- raylib 5.5 开发文件及 `pkg-config` 元数据
- 图形显示环境

```bash
make
make run
```

`make` 生成 `./pingpong`，`make clean` 删除它。可以用以下命令检查 raylib 版本：

```bash
pkg-config --modversion raylib
```

### 项目结构

```text
main.cpp              Entrypoint and window loop
game.cpp / game.h     Game state, input, collisions, rendering
components/           Paddle, Ball, Line, Velocity
Makefile              Build and run targets
```

## English

### Overview

A two-player Pong demo written in C++17 with raylib 5.5. It includes two paddles, a bouncing ball, boundary collisions, pause support, and a start screen. The round ends when the ball crosses the left or right boundary.

### Controls

| Key | Action |
| --- | --- |
| `W` / `S` | Move left paddle up / down |
| `Up` / `Down` | Move right paddle up / down |
| `Space` | Pause / resume |
| `G` | Start the game from the start screen |
| `Esc` | Quit from the start screen |

### Build and run

Requirements:

- A C++17 compiler (`g++`)
- `make`
- raylib 5.5 development files with `pkg-config` metadata
- A graphical display

```bash
make
make run
```

`make` builds `./pingpong`; `make clean` removes it. Check the raylib version with:

```bash
pkg-config --modversion raylib
```

## License

MIT
