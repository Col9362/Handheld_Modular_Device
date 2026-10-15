# Handheld Modular Device

A handheld built around hot-swappable control modules. Modules attach to the base unit
through an 8-pin pogo connector, and the base detects which module is attached
over I2C plus a resistor-divider ID line.

More details and photos: https://colezuckerman.com/projects/modular-handheld/

## Repository layout

| Folder | Contents |
|---|---|
| `base/` | KiCad project for the base unit (Raspberry Pi Pico, display connector, buzzers, pogo connector) |
| `base/gerbers/` | Manufacturing files for the base unit PCB |
| `base/backup-2026-06-27/` | Earlier snapshot of the base unit KiCad project |
| `gaming-module/` | Gaming controller module (MCP23017 buttons, joystick, haptics) |
| `gaming-module/gerbers/` | Manufacturing files for the gaming module PCB |
| `firmware/` | MicroPython code that runs on the base unit's Pico |

### Gaming module note

The original KiCad project files for the gaming module were lost. The Gerbers in
`gaming-module/gerbers/` are the exact files the board was manufactured from.
`schematic.png` is a screenshot of the original schematic, and `preview-top.png` /
`preview-bottom.png` are renders of the board.

## Firmware

Copy everything in `firmware/` to the root of the Pico's filesystem (for example with
Thonny). `main.py` runs at boot.
