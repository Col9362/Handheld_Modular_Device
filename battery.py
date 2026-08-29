from machine import Pin, ADC, PWM
import display as d
import st7789py as st7789
import battery_font2 as font
import utime

vsys = ADC(Pin(29))
charging_pin = Pin(24, Pin.IN, Pin.PULL_DOWN)

conversion_factor = 3 * 3.3 / 65535
full_battery = 4.2
empty_battery = 2.8

last_check_time = 0
CHECK_INTERVAL = 120000

last_percentage = -1
last_charging = None

charging_changed = False
last_charging_time = 0

def get_percentage():
    total = 0
    samples = 10
    for _ in range(samples):
        total += vsys.read_u16()
        utime.sleep_ms(5)
    avg_reading = total / samples
    voltage = avg_reading * conversion_factor
    percentage = 100 * ((voltage - empty_battery) / (full_battery - empty_battery))
    percentage = max(0, min(100, percentage))
    return round(percentage)

def is_charging():
    return charging_pin.value() == 1

def draw_indicator():
    global last_percentage, last_charging
    percentage = get_percentage()
    charging = is_charging()
    last_percentage = percentage
    last_charging = charging

    text = str(percentage) + "%"
    if charging:
        text = "*** " + text

    max_text = "*** 100%"
    max_width = font.MAX_WIDTH * len(max_text)
    x = 320 - max_width - 5
    y = 5

    d.display.fill_rect(x - 2, y - 2, max_width + 4, font.HEIGHT + 4, st7789.BLACK)

    text_width = font.MAX_WIDTH * len(text)
    text_x = 320 - text_width - 5
    d.display.write(font, text, text_x, y, st7789.WHITE, st7789.BLACK)

def periodic_check():
    global last_check_time
    now = utime.ticks_ms()
    elapsed = utime.ticks_diff(now, last_check_time)
    if elapsed > CHECK_INTERVAL:
        last_check_time = now
        percentage = get_percentage()
        charging = is_charging()
        if percentage != last_percentage or charging != last_charging:
            draw_indicator()

def set_charging_flag(pin):
    global charging_changed, last_charging_time
    now = utime.ticks_ms()
    elapsed = utime.ticks_diff(now, last_charging_time)
    if elapsed > 300:
        last_charging_time = now
        charging_changed = True

charging_pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=set_charging_flag)