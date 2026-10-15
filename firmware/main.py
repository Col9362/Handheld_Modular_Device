from machine import Pin, ADC, PWM
import utime
import button
import joystick
import home_screen
import game_menu
import display
import settings
import tetris
import battery

buzzer = PWM(Pin(21))
def beep(duration_ms, freq, volume):
    buzzer.freq(freq)
    buzzer.duty_u16(volume)
    utime.sleep_ms(duration_ms)
    buzzer.duty_u16(0)

id_pin = ADC(26)
module_int_pin = Pin(18, Pin.IN, Pin.PULL_UP)
module_detect = False
last_module_time = 0
module_ids = [3.3, 2.2]
modules = ["none", "gaming"]
current_module = "none"

def set_module_flag(pin):
    global last_module_time, module_detect
    now = utime.ticks_ms()
    elapsed = utime.ticks_diff(now, last_module_time)
    if elapsed > 300:
        last_module_time = now
        module_detect = True

def update_connected_module():
    global module_detect, current_module
    module_detect = False
    module_int_pin.irq(handler=None)
    button.set_module_present(False)

    utime.sleep_ms(200)

    id_voltage = id_pin.read_u16() * 3.3 / 65535
    new_module = "none"
    for index, mid in enumerate(module_ids):
        if abs(mid - id_voltage) < 0.2:
            new_module = modules[index]
            break

    if new_module == "none":
        current_module = "none"
        button.set_module_present(False)
    elif new_module == "gaming":
        success = False
        for attempt in range(5):
            try:
                button.reinit_mcp()
                joystick.reint_ads()
                success = True
                break
            except Exception:
                utime.sleep_ms(100)
        if success:
            current_module = new_module
            button.set_module_present(True)
        else:
            current_module = "none"
            button.set_module_present(False)
    
    
    home_screen.update(current_module)
    
    if game_menu.GAME_MENU_OPEN and current_module != "gaming":
        game_menu.GAME_MENU_OPEN = False
        home_screen.HOME_OPEN = True
        home_screen.open_home()
        
    elif home_screen.HOME_OPEN == True: 
        home_screen.draw()

    utime.sleep_ms(100)
    module_int_pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=set_module_flag)



module_int_pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=set_module_flag)


update_connected_module()


while True:
    if module_detect:
        update_connected_module()
        
    if battery.charging_changed:
        battery.charging_changed = False
        battery.draw_indicator()
    battery.periodic_check()
    if current_module == "gaming":
        
        events = button.button_check()
        joystick_state = joystick.joystick_state()
        held_events = button.button_hold_check(300)
        if home_screen.HOME_OPEN:
            if events:
                pressed_pins = [pin for pin, is_pressed in events.items() if is_pressed]
                for btn in pressed_pins:
                    home_screen.change_selected(btn)
            if held_events:
                for btn in held_events:
                    home_screen.change_selected(btn)
                
            if joystick_state != "NONE":
                    home_screen.change_selected(joystick_state)
        elif game_menu.GAME_MENU_OPEN:
            if events:
                pressed_pins = [pin for pin, is_pressed in events.items() if is_pressed]
                for btn in pressed_pins:
                    game_menu.change_selected(btn)
            if held_events:
                for btn in held_events:
                    game_menu.change_selected(btn)
                
            if joystick_state != "NONE":
                    game_menu.change_selected(joystick_state)
        elif settings.SETTINGS_OPEN:
            if events:
                pressed_pins = [pin for pin, is_pressed in events.items() if is_pressed]
                for btn in pressed_pins:
                    settings.process_input(btn)
            if held_events:
                for btn in held_events:
                    settings.process_input(btn)
                
            if joystick_state != "NONE":
                    settings.process_input(joystick_state)
        elif tetris.TETRIS_OPEN:
            if events:
                pressed_pins = [pin for pin, is_pressed in events.items() if is_pressed]
                for btn in pressed_pins:
                    tetris.process_input(btn)
            if held_events:
                for btn in held_events:
                    tetris.process_input(btn)
                
            if joystick_state != "NONE":
                    tetris.process_input(joystick_state)
                    
            down_held = ("DOWN" in held_events) or (joystick_state == "DOWN")
            if not down_held:
                tetris.stop_accelerating()
                        
            if tetris.GAME_STATUS:
                tetris.gravity_check()
        
    utime.sleep_ms(100)
    
    
    
    