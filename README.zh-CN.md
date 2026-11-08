# Pingpong

[English](README.md) | 简体中文

一个使用 C++17 和 [raylib](https://www.raylib.com/) 5.5 编写的双人 Pong demo。

## 简介

Pingpong 包含左右球拍、球的反弹、边界碰撞、碰撞音效、暂停功能和开始界面。球越过左边界或右边界时本局结束。

## 操作

| 操作 | 功能 |
| --- | --- |
| `W` / `S` | 左球拍上移 / 下移 |
| `↑` / `↓` | 右球拍上移 / 下移 |
| `Space` | 在开始界面开始游戏；游戏中暂停 / 继续 |
| `Esc` / 关闭窗口 | 在开始界面退出 |

## 依赖

- C++17 编译器（`g++`）
- `make`
- raylib 5.5 开发文件及 `pkg-config` 元数据
- 图形显示环境

## 构建与运行

```bash
make
make run
```

`make` 生成 `./pingpong`，`make clean` 删除它。可以用以下命令检查 raylib 版本：

```bash
pkg-config --modversion raylib
```

请在项目根目录运行游戏，以便正确加载 `sounds/` 下的相对路径音效。

## 项目结构

```text
main.cpp              程序入口和窗口循环
game.cpp / game.h     游戏状态、输入、碰撞和渲染
components/           Paddle、Ball、Line、Velocity
sounds/               WAV 音效
Makefile              构建和运行目标
```

## 许可证

MIT
