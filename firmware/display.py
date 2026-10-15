from machine import Pin, SPI, PWM
import st7789py as st7789
import vga2_8x8 as font
import math

spi = SPI(1, baudrate=40000000, polarity=0, phase=0, sck=Pin(10), mosi=Pin(11))

backlight = PWM(Pin(15))
backlight.freq(1000)
backlight.duty_u16(round(65535 * 1))


display = st7789.ST7789(
    spi,
    240,
    320,
    reset=Pin(13, Pin.OUT),
    cs=Pin(9, Pin.OUT),
    dc=Pin(14, Pin.OUT),
    backlight=None,
    rotation=3
)


def set_brightness(percent):
    duty = round((percent / 100) * 65535)
    backlight.duty_u16(duty)



def fill_rounded_rect(x, y, w, h, radius, color, bg_color):
    display.fill_rect(x, y, w, h, color)
    for i in range(radius):
        dy = radius - i
        dx = radius - math.sqrt(radius * radius - dy * dy)
        cut = round(dx)
        for j in range(cut):
            display.pixel(x + j, y + i, bg_color)
            display.pixel(x + w - 1 - j, y + i, bg_color)
            display.pixel(x + j, y + h - 1 - i, bg_color)
            display.pixel(x + w - 1 - j, y + h - 1 - i, bg_color)
            
def thick_rect(x, y, w, h, thickness, color):
    for i in range(thickness):
        display.rect(x + i, y + i, w - 2 * i, h - 2 * i, color)


def fill_triangle(x1, y1, x2, y2, x3, y3, color):
    points = sorted([(x1,y1), (x2,y2), (x3,y3)], key=lambda p: p[1])
    (ax, ay), (bx, by), (cx, cy) = points
    for y in range(ay, cy + 1):
        xa = ax + (cx - ax) * (y - ay) / (cy - ay) if cy != ay else ax
        if y < by:
            xb = ax + (bx - ax) * (y - ay) / (by - ay) if by != ay else ax
        else:
            xb = bx + (cx - bx) * (y - by) / (cy - by) if cy != by else bx
        left, right = sorted([round(xa), round(xb)])
        display.hline(left, y, right - left + 1, st7789.WHITE if color is None else color)

# test
fill_triangle(50, 50, 50, 70, 70, 60, st7789.CYAN)