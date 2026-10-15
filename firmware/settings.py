import st7789py as st7789
import pressstart2p_8 as font
import pressstart2p_24 as titlefont
import pressstart2p_12 as itemfont
import display as d
import home_screen
import utime
import urandom
import button
import storage
import math
import battery

SETTINGS_OPEN = False


def open_settings():
    global SETTINGS_OPEN
    
    SETTINGS_OPEN = True
    draw_settings_menu()

def close_settings():
    global SETTINGS_OPEN
    
    update_settings()
    SETTINGS_OPEN = False
    home_screen.open_home()

menu_positions = {
    0: "back",
    1: "mute",
    2: "volume",
    3: "brightness",
    4: "hold_delay"
}

menu_items = {
    "back": {"name": "Back", "type": "button", "link": close_settings},
    "mute": {"name": "Mute", "type": "toggle"},
    "volume": {"name": "Volume", "type": "number", "min": 0, "max": 100},
    "brightness": {"name": "Brightness", "type": "number", "min": 15, "max": 100},
    "hold_delay": {"name": "Hold Delay", "type": "number", "min": 150, "max": 600}
}

menu_item_length = 60
menu_item_height = 20
menu_selected = 0

settings = {
    "mute": False,
    "volume": 20,
    "brightness": 80,
    "hold_delay": 300
}



def brightness_update(brightness):
    d.set_brightness(brightness)

def update_variables():
    global settings
    settings_items = storage.retrieve_settings_list()
    for item in settings_items:
        settings[item] = storage.retrieve_setting[item]
        
    brightness_update(settings["brightness"])
         
         
def retrieve_volume():
    update_variables()
    return settings["volume"], settings["mute"]


        
def update_settings():
    for item in settings:
        storage.save_setting(item, settings[item])
        
        

start_x = 30
start_y = 50
separation_distance = 25

def draw_selection_indicator(item, curr_select):
    top = start_y + (item * separation_distance)
    bottom = top + itemfont.HEIGHT - 4
    mid = round(top + ((itemfont.HEIGHT - 4) / 2 ))
    if curr_select:
        d.fill_triangle(10, top, 10, bottom, 18, mid, st7789.CYAN)
    else:
        d.fill_triangle(10, top, 10, bottom, 18, mid, st7789.BLACK)
        
        
def draw_settings_data():
    for index, item in menu_positions.items():
        if index == 0:
            continue
        d.display.fill_rect(200, start_y + (index * separation_distance), 60, itemfont.HEIGHT, st7789.BLACK)
        d.display.write(itemfont, str(settings[item]), 200, start_y + (index * separation_distance), st7789.WHITE, st7789.BLACK)
        
def draw_settings_menu():
    d.display.fill(st7789.BLACK)
    battery.draw_indicator()
    for index, item in menu_positions.items():
        d.display.write(itemfont, menu_items[item]["name"], start_x, start_y + (index * separation_distance), st7789.WHITE, st7789.BLACK)
    draw_selection_indicator(menu_selected, True)
    
    draw_settings_data()
draw_settings_menu()

def change_setting(positive):
    setting = menu_positions[menu_selected]
    setting_type = menu_items[menu_positions[menu_selected]]["type"]
    if positive:
        
        if(setting_type == "toggle"):
            settings[setting] = True
        elif (setting_type == "number"):
            if not (settings[setting] + 1 > menu_items[setting]["max"]):
                settings[setting] = settings[setting] + 1

    else:
        if(setting_type == "toggle"):
            settings[setting] = False
        elif (setting_type == "number"):
            if not (settings[setting] - 1 < menu_items[setting]["min"]):
                settings[setting] = settings[setting] - 1
                    
    draw_settings_data()


def process_input(button):
    global menu_selected
    old_menu_selected = menu_selected
    if button == "UP":
        if old_menu_selected == 0:
            return
        else:
            menu_selected -= 1
            draw_selection_indicator(old_menu_selected, False)
            draw_selection_indicator(menu_selected, True)
    elif button == "DOWN":
        if old_menu_selected == (len(menu_positions) - 1):
            return
        else:
            menu_selected += 1
            draw_selection_indicator(old_menu_selected, False)
            draw_selection_indicator(menu_selected, True)
    elif button == "S3" and old_menu_selected == 0:
        close_settings()
    elif button == "LEFT":
        change_setting(False)
    elif button == "RIGHT":
        change_setting(True)
    
