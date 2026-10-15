from machine import Pin, SoftI2C
import utime
import mcp23017

scl = Pin(17, Pin.OPEN_DRAIN, Pin.PULL_UP)
sda = Pin(16, Pin.OPEN_DRAIN, Pin.PULL_UP)
i2c = SoftI2C(scl=scl, sda=sda, freq=10000)

button_values = {
    0: "UP", 1: "RIGHT", 2: "DOWN", 3: "LEFT",
    4: "S1", 5: "S2", 6: "S3", 7: "JOYSTICK_BUTTON"
}

button_last_ms = {b: 0 for b in button_values}
button_pressed = {b: False for b in button_values}
button_held = {b: False for b in button_values}
button_detect = False
last_button_ms = 0

module_present = False
mcp = None
mcp_int_pin = Pin(19, Pin.IN, Pin.PULL_UP)

def reconfigure_pins():
    mcp.config(
        interrupt_mirror=False,
        interrupt_open_drain=False,
        interrupt_polarity=0
    )
    for pin_num in button_values:
        mcp.pin(pin_num, mode=1, pullup=True, interrupt_enable=True, interrupt_compare_default=False)

def reinit_mcp():
    global mcp
    mcp = mcp23017.MCP23017(i2c, 0x20)
    reconfigure_pins()

def set_module_present(value):
    global module_present
    module_present = value

def set_button_flag(pin):
    global button_detect, last_button_ms, button_fire_count
    now = utime.ticks_ms()
    elapsed = utime.ticks_diff(now, last_button_ms)
    if elapsed > 20:
        button_detect = True
        last_button_ms = now

mcp_int_pin.irq(trigger=Pin.IRQ_FALLING, handler=set_button_flag)

def button_check():
    global button_detect, button_pressed
    events = {}
    if not module_present:
        return "no module detected"
    if button_detect == False:
        return events
    button_detect = False
    state = mcp.porta.gpio
    for pin_num in button_values:
        bit_value = state & (1 << pin_num)
        is_pressed = (bit_value == 0)
        if button_pressed[pin_num] != is_pressed:
            events[button_values[pin_num]] = is_pressed
            button_pressed[pin_num] = is_pressed
            if (is_pressed == False and button_held[pin_num] == True):
                button_held[pin_num] = False
                continue
            if (is_pressed == True):
                 button_last_ms[pin_num] = utime.ticks_ms()
    return events

def button_hold_check(hold_delay):
    global button_held
    held_events = []
    if not module_present:
        return held_events
    now = utime.ticks_ms()
    for pin_num in button_values:
        elapsed = utime.ticks_diff(now, button_last_ms[pin_num])
        if ((button_pressed[pin_num] == True) and (elapsed > hold_delay)):
            button_held[pin_num] = True
            held_events.append(button_values[pin_num])
    return held_events

