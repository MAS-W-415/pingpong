# Pingpong

[English](README.md) | 简体中文

一个使用 C++17 和 [raylib](https://www.raylib.com/) 5.5 编写的双人 Pong demo。

## 简介

Pingpong 包含左右球拍、弹跳球、边界碰撞、碰撞音效和开始界面。游戏使用一张
合并精灵图：梦幻蓝天背景、泡泡球、云朵球拍、尾迹帧和泡泡破裂动画。

## 操作

| 操作 | 功能 |
| --- | --- |
| `W` / `S` | 左球拍上移 / 下移 |
| `↑` / `↓` | 右球拍上移 / 下移 |
| `Space` | 在开始界面开始游戏 |
| `Esc` / 关闭窗口 | 退出 |

## 依赖

- C++17 编译器（GCC 或 Clang；Makefile 会强制包含本地 `raylib.h` overlay）
- `make`
- raylib 5.5 开发文件及 `pkg-config` 元数据
- 图形显示环境

## 构建与运行

```bash
make
make run
```

`make` 生成 `./pingpong`，`make clean` 删除它。根目录或 `components/` 下新增的
`.cpp` 文件会被自动编译。

可以用以下命令检查 raylib 版本：

```bash
pkg-config --modversion raylib
```

请在项目根目录运行游戏，以便正确加载 `assets/` 和 `sounds/` 下的相对路径资源。

## 项目结构

```text
main.cpp                  程序入口和窗口循环
game.cpp / game.h         游戏状态、输入、碰撞、渲染和状态流程
components/               实体、碰撞、输入、资源加载和音效辅助代码
assets/pingpong-art/      合并精灵图、资源清单、构建脚本和美术说明
assets/pingpong-art.tar.gz
sounds/                   WAV 音效
raylib.h                  本地 raylib overlay 头文件
Makefile                  构建和运行目标
```

合并美术资源的详细说明见
[`assets/pingpong-art/README.md`](assets/pingpong-art/README.md)。其中
`pingpong-art.spritepos` 使用空格分隔的 `[meta]`、`[frames]` 和
`[animations]` 段；`build.py` 会同时生成 PNG 和清单。

当前使用的音效：

- `sounds/bounce.wav`
- `sounds/paddle2wall.wav`
- `sounds/pop.wav`

## 版本

[v1.0.0](https://github.com/MAS-W-415/pingpong/releases/tag/v1.0.0)

不提供预编译二进制或可下载的构建产物；请使用 `make` 从源码构建。

## 许可证

源代码使用 MIT 许可证。`assets/pingpong-art/` 下的合并美术资源使用
CC0-1.0；详见该目录的 `LICENSE` 文件。
