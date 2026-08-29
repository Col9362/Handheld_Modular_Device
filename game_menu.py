from machine import Pin
import st7789py as st7789
import pressstart2p_8 as font
import display as d
import home_screen
import tetris
import battery

BACKGROUND_COLOR = st7789.BLACK
GAME_MENU_OPEN = False

positions = {
    (0,0): "back",
    (0,1): "tetris",
    (0,2): "blocks",
    (1,2): "snake",
    (1,1): "chess",
    (1,0): "placeholder"
}

apps = {
    "back": {"name": "BACK", "color": home_screen.dim_color(st7789.RED, 0.5), "link": home_screen.open_home},
    "tetris": {"name": "Tetris", "color": st7789.CYAN, "link": tetris.open_tetris_menu},
    "blocks": {"name": "Notes", "color": home_screen.dim_color(st7789.YELLOW, 0.75)},
    "snake": {"name": "Settings", "color": st7789.MAGENTA},
    "chess": {"name": "Stopwatch", "color": home_screen.dim_color(st7789.RED, 0.8)},
    "placeholder": {"name": "Coin Flip", "color": st7789.BLUE}
}

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
        fill_color = app["color"]
       
        d.display.fill_rect(x, y, BOX_SIZE, BOX_SIZE, fill_color)
        
        text_x = round(x + (BOX_SIZE - (font.MAX_WIDTH * len(app["name"]))) / 2)
        text_y = round(y + ((BOX_SIZE - font.HEIGHT) / 3))
        d.display.write(font, app["name"], text_x, text_y, st7789.WHITE, fill_color)
        
        if pos == selected:
            d.thick_rect(x - 1, y - 1, BOX_SIZE + 2, BOX_SIZE + 2, 2, st7789.WHITE)
            
def draw_box(row, col, curr_select):
    x = MARGIN + col * (BOX_SIZE + GAP)
    y = MARGIN + row * (BOX_SIZE + GAP)
    if curr_select:
        d.thick_rect(x - 1, y - 1, BOX_SIZE + 2, BOX_SIZE + 2, 2, st7789.WHITE)
    else:
        d.thick_rect(x - 1, y - 1, BOX_SIZE + 2, BOX_SIZE + 2, 2, BACKGROUND_COLOR)
    
    
def open_selected():
    global GAME_MENU_OPEN
    app = positions[selected]
    GAME_MENU_OPEN = False
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


def open_menu():
    global GAME_MENU_OPEN
    GAME_MENU_OPEN = True
    draw()
    
    