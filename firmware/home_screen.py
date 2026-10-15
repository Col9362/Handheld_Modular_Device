from machine import Pin
import st7789py as st7789
import pressstart2p_8 as font
import display as d
import settings
import battery

BACKGROUND_COLOR = st7789.BLACK

def dim_color(color, factor):
    red = (color >> 11) & 0x1F
    green = (color >> 5) & 0x3F
    blue = color & 0x1F
    
    dimmed_red = round(red * factor)
    dimmed_green = round(green * factor)
    dimmed_blue = round(blue * factor)
    
    dimmed_color = (dimmed_red << 11) | (dimmed_green << 5) | dimmed_blue
    return dimmed_color


positions = {
    (0,0): "gaming",
    (0,1): "music",
    (0,2): "notepad",
    (1,2): "settings",
    (1,1): "stopwatch",
    (1,0): "coinflip"
}

HOME_OPEN = True

def open_game_menu():
    global HOME_OPEN
    
    HOME_OPEN = False
    import game_menu
    game_menu.open_menu()
    
def open_settings():
    global HOME_OPEN
    
    HOME_OPEN = False
    import settings
    settings.open_settings()


apps = {
    "gaming": {"name": "Games", "connected": False, "color": dim_color(st7789.GREEN, 0.8), "link": open_game_menu},
    "music": {"name": "Music", "connected": False, "color": st7789.CYAN},
    "notepad": {"name": "Notes", "connected": False, "color": st7789.YELLOW},
    "settings": {"name": "Settings", "connected": True, "color": st7789.MAGENTA, "link": open_settings},
    "stopwatch": {"name": "Stopwatch", "connected": True, "color": dim_color(st7789.RED, 0.8)},
    "coinflip": {"name": "Coin Flip", "connected": True, "color": st7789.BLUE}
}

def update(current_module):
    global apps
    for app in apps:
        if app == "settings" or app == "stopwatch" or app == "coinflip" :
            continue
        apps[app]["connected"] = False
    if current_module != "none":
        apps[current_module]["connected"] = True
        
        
        
MARGIN = 15
GAP = 15
BOX_SIZE = 90
selected = (0,0)
        
def draw():
    d.display.fill(BACKGROUND_COLOR)
    battery.draw_indicator()
    for pos, module_name in positions.items():
        row, col = pos
        x = MARGIN + col * (BOX_SIZE + GAP)
        y = MARGIN + row * (BOX_SIZE + GAP)
        app = apps[module_name]
        if app["connected"]:
            fill_color = app["color"]
        else:
            fill_color = dim_color(app["color"], 0.1)
            
        d.display.fill_rect(x, y, BOX_SIZE, BOX_SIZE, fill_color)
        
        text_x = round(x + (BOX_SIZE - (font.MAX_WIDTH * len(app["name"]))) / 2)
        text_y = round(y + ((BOX_SIZE - font.HEIGHT) / 3))
        d.display.write(font, app["name"], text_x, text_y, st7789.WHITE, fill_color)
        
        if pos == selected:
            d.thick_rect(x - 1, y - 1, BOX_SIZE + 2, BOX_SIZE + 2, 2, st7789.WHITE)
draw()
    
def draw_box(row, col, curr_select):
    x = MARGIN + col * (BOX_SIZE + GAP)
    y = MARGIN + row * (BOX_SIZE + GAP)
    if curr_select:
        d.thick_rect(x - 1, y - 1, BOX_SIZE + 2, BOX_SIZE + 2, 2, st7789.WHITE)
    else:
        d.thick_rect(x - 1, y - 1, BOX_SIZE + 2, BOX_SIZE + 2, 2, BACKGROUND_COLOR)
    
    
def open_selected():
    global HOME_OPEN
    app = positions[selected]
    if apps[app]["connected"]:
        HOME_OPEN = False
        apps[app]["link"]()
        
    
    
def change_selected(movement):
    global selected
    old_row, old_col = selected
    row, col = selected
    if movement == "UP":
        if old_row == 1:
            row = 0
    elif movement == "DOWN":
        if old_row == 0:
            row = 1
    elif movement == "LEFT":
        if old_col > 0:
            col -= 1
    elif movement == "RIGHT":
        if old_col < 2:
            col += 1
    elif movement == "S3":
        open_selected()
        return
    if (row == old_row) and (col == old_col):
        return
    draw_box(old_row, old_col, False)
    selected = (row,col)
    draw_box(row, col, True)
    
    
def open_home():
    global HOME_OPEN
    global selected
    HOME_OPEN = True
    selected = (0,0)
    draw()
    
