import st7789py as st7789
import pressstart2p_8 as font
import pressstart2p_24 as titlefont
import pressstart2p_12 as itemfont
import display as d
from home_screen import dim_color as dim
import utime
import urandom
import button
import storage
import math
import battery

import tetris_song

CELL_SIZE = 10
COLS = 10
ROWS = 20
GRID_X = 110
GRID_Y = 30

TETRIS_OPEN = False
GAME_STATUS = False

GRAVITY_ACCELERATED = False

GAME_OVER_OPEN = False

board = []
for r in range(ROWS):
    board.append([-1 for c in range(COLS)])
    
pieces = {
 "I": {"color": st7789.CYAN, "horizontal_count": 4, "vertical_count": 0, "box_size": 4, "shape": [[(0,0), (0,1), (0,2), (0,3)], [(0,0), (1,0), (2,0), (3,0)], [(0,0), (0,1), (0,2), (0,3)], [(0,0), (1,0), (2,0), (3,0)]]},
 "O": {"color": st7789.YELLOW, "box_size": 2, "horizontal_count": 2, "vertical_count": 2, "shape": [[(0,0),(0,1),(1,0),(1,1)]] * 4},
 "T": {"color": d.st7789.color565(160,32,240), "box_size": 3, "horizontal_count": 3, "vertical_count": 2,"shape": [[(0,0),(0,1),(0,2),(1,1)], [(-1,1),(0,0),(0,1),(1,1)], [(-1,1),(0,0),(0,1),(0,2)], [(-1,1),(0,1),(0,2),(1,1)]]},
 "S": {"color": st7789.GREEN, "box_size": 3, "horizontal_count": 3, "vertical_count": 2, "shape": [[(0,1),(0,2),(1,0),(1,1)], [(-1,2),(0,1),(0,2),(1,1)], [(0,0),(0,1),(1,1),(1,2)], [(-1,2),(0,1),(0,2),(1,1)]]},
 "Z": {"color": st7789.RED, "box_size": 3, "horizontal_count": 3, "vertical_count": 2, "shape": [[(0,0),(0,1),(1,1),(1,2)], [(-1,1),(0,0),(0,1),(1,0)], [(0,0),(0,1),(1,1),(1,2)], [(-1,1),(0,0),(0,1),(1,0)]]},
 "J": {"color": st7789.BLUE, "box_size": 3, "horizontal_count": 2, "vertical_count": 3, "shape": [[(0,1),(1,1),(2,0),(2,1)], [(0,0),(1,0),(1,1),(1,2)], [(0,1),(0,2),(1,1),(2,1)], [(1,0),(1,1),(1,2),(2,2)]]},
 "L": {"color": d.st7789.color565(255,140,0), "box_size": 3, "horizontal_count": 4, "vertical_count": 3, "shape": [[(0,1),(1,1),(2,1),(2,2)], [(1,0),(1,1),(1,2),(2,0)], [(0,0),(0,1),(1,1),(2,1)], [(0,2),(1,0),(1,1),(1,2)]]}
}

current_piece = ""
next_piece = ""

current_pos = (0,3)
current_rotation = 0

last_fall_time = 0
gravity_time = 450
score = 0
clears_in_a_row = 0

gravity_multiplier = 1

def trigger_game_start():
    start_game()

def leave_tetris():
    import game_menu
    TETRIS_OPEN = False
    game_menu.open_menu()
    


menu_positions = {
    0: "play",
    1: "back"
}

menu_items = {
    "play": {"name": "Play", "link": trigger_game_start},
    "back": {"name": "Back", "link": leave_tetris}
}

menu_item_length = 80
menu_item_height = 40
menu_selected = 0

def draw_selected_box(item, curr_select):
    x = round((320 - menu_item_length)/2)
    y = 120 + (50 * item)
    if curr_select:
        d.thick_rect(x - 1, y - 1, menu_item_length + 2, menu_item_height + 2, 4, st7789.CYAN)
    else:
        d.thick_rect(x - 1, y - 1, menu_item_length + 2, menu_item_height + 2, 4, st7789.BLACK)

def open_selected():
    item = menu_positions[menu_selected]
    menu_items[item]["link"]()

def draw_menu():
    d.display.fill(st7789.BLACK)
    battery.draw_indicator()
    d.fill_rounded_rect(70, 20, 180, 80, 20, st7789.WHITE, st7789.BLACK)

    text_x = round(70 + (180 - (titlefont.MAX_WIDTH * len("Tetris"))) / 2)
    text_y = round(20 + ((80 - titlefont.HEIGHT) / 2))
    d.display.write(titlefont, "Tetris", text_x, text_y, st7789.BLACK, st7789.WHITE)
    
    for pos, item_name in menu_positions.items():
        
        x = round((320 - menu_item_length)/2)
        y = 120 + (50 * pos)
        item = menu_items[item_name]
        d.display.fill_rect(x, y, menu_item_length, menu_item_height, st7789.WHITE)
        
        text_x = round(x + (menu_item_length - (itemfont.MAX_WIDTH * len(item["name"]))) / 2)
        text_y = round(y + ((menu_item_height - itemfont.HEIGHT) / 2))
        d.display.write(itemfont, item["name"], text_x, text_y, st7789.BLACK, st7789.WHITE)
        
        if pos == menu_selected:
            d.thick_rect(x - 1, y - 1, menu_item_length + 2, menu_item_height + 2, 4, st7789.CYAN)
        



def open_tetris_menu():
    global GAME_STATUS, TETRIS_OPEN, GAME_OVER_OPEN
    
    tetris_song.stop_music()
    TETRIS_OPEN = True
    GAME_STATUS = False
    GAME_OVER_OPEN = False
    draw_menu()

def draw_grid():
    d.display.fill(st7789.BLACK)
    battery.draw_indicator()
    for row in range(ROWS):
        for col in range(COLS):
            x = GRID_X + col * CELL_SIZE
            y = GRID_Y + row * CELL_SIZE
            d.display.rect(x,y, CELL_SIZE, CELL_SIZE, st7789.WHITE)
            
            
            

def draw_piece():
    y,x = current_pos
    x *= CELL_SIZE
    y *= CELL_SIZE
    x += GRID_X
    y += GRID_Y
    piece = pieces[current_piece]
    for row, col in piece["shape"][current_rotation]:
        d.display.fill_rect(x + 1 + col * CELL_SIZE, y + 1 + row * CELL_SIZE, CELL_SIZE - 2, CELL_SIZE - 2, piece["color"])
      
      

def erase_piece(rotation):
    y,x = current_pos
    x *= CELL_SIZE
    y *= CELL_SIZE
    x += GRID_X
    y += GRID_Y
    piece = pieces[current_piece]
    for row, col in piece["shape"][rotation]:
        d.display.fill_rect(x + 1 + col * CELL_SIZE, y + 1 + row * CELL_SIZE, CELL_SIZE - 2, CELL_SIZE - 2, st7789.BLACK)
        
def spawn_piece():
    global current_piece, next_piece, current_pos, current_rotation
    
    current_piece = next_piece
    
    draw_next_piece(True)
    
    next_piece = urandom.choice(list(pieces.keys()))
    
    draw_next_piece(False)
    
    current_pos = (0,3)
    current_rotation = 0
                        
                        
def check_highscore(score):
    highscore = storage.get_tetris_highscore()
    old_highscore = highscore
    if score > highscore:
        storage.save_highscore("tetris", score)
        return True, old_highscore
    return False, old_highscore

                        
def game_over():
    global GAME_STATUS, GAME_OVER_OPEN
    GAME_STATUS = False
    GAME_OVER_OPEN = True
    
    tetris_song.play_game_over()
    
    d.fill_rounded_rect(85, 50, 150, 100, 5, st7789.WHITE, st7789.BLACK)
    
    text_x = round(85 + (150 - (itemfont.MAX_WIDTH * len("Game Over"))) / 2)
    text_y = round(50 + ((100 - itemfont.HEIGHT) / 8))
    d.display.write(itemfont, "Game Over", text_x, text_y, st7789.BLACK, st7789.WHITE)
    
    text_x = round(85 + (150 - (font.MAX_WIDTH * len("Your Score: " + str(score)))) / 2)
    text_y = round(80 + ((100 - font.HEIGHT) / 6))
    d.display.write(font, "Your Score: " + str(score), text_x, text_y, st7789.BLACK, st7789.WHITE)
    
    
    
    new_highscore, highscore = check_highscore(score)

    text_x = round(85 + (150 - (font.MAX_WIDTH * len("Highscore: " + str(highscore)))) / 2)
    text_y = round(100 + ((100 - font.HEIGHT) / 6))
    d.display.write(font, "Highscore: " + str(highscore), text_x, text_y, st7789.BLACK, st7789.WHITE)
    

    if new_highscore:
        d.fill_rounded_rect(100, 160, 120, 50, 5, st7789.YELLOW, st7789.BLACK)
        
        text_x = round(100 + (120 - (font.MAX_WIDTH * len("New Highscore!"))) / 2)
        text_y = round(170 + ((50 - font.HEIGHT) / 8))
        d.display.write(font, "New Highscore!", text_x, text_y, st7789.BLACK, st7789.YELLOW)
        
        text_x = round(100 + (120 - (font.MAX_WIDTH * len(str(score)))) / 2)
        text_y = round(185 + ((50 - font.HEIGHT) / 8))
        d.display.write(font, str(score), text_x, text_y, st7789.BLACK, st7789.YELLOW)
        
    



def is_valid_position(shape, position):
    for piece in shape:
        y,x = piece
        y_pos, x_pos = position
        prop_x = x_pos + x
        prop_y = y_pos + y
        if (prop_x < 0) or (prop_x >= COLS) or (prop_y < 0) or (prop_y >= ROWS) or (board[prop_y][prop_x] != -1):
            return False
    return True

def lock_piece():
    global GAME_STATE
    
    for box in pieces[current_piece]["shape"][current_rotation]:
        y,x = box
        y_pos, x_pos = current_pos
        x_real = x_pos + x
        y_real = y_pos + y
        board[y_real][x_real] = pieces[current_piece]["color"]
    if GAME_STATUS:
        check_complete_rows()
        spawn_piece()
        if not is_valid_position(pieces[current_piece]["shape"][current_rotation], current_pos):
            game_over()


def move_down():
    global current_pos
    y,x = current_pos
    new_y = y + 1
    if is_valid_position(pieces[current_piece]["shape"][current_rotation], (new_y,x)):
        erase_piece(current_rotation)
        current_pos = (new_y,x)
        draw_piece()
    else:
        lock_piece()
        

def move_left():
    global current_pos
    y,x = current_pos
    new_x = x - 1
    if is_valid_position(pieces[current_piece]["shape"][current_rotation], (y,new_x)):
        erase_piece(current_rotation)
        current_pos = (y,new_x)
        draw_piece()
        
def move_right():
    global current_pos
    y,x = current_pos
    new_x = x + 1
    if is_valid_position(pieces[current_piece]["shape"][current_rotation], (y,new_x)):
        erase_piece(current_rotation)
        current_pos = (y,new_x)
        draw_piece()
        
def accelerate_down():
    global gravity_time, score, GRAVITY_ACCELERATED
    score += 1
    GRAVITY_ACCELERATED = True
    draw_score()
    gravity_time = 120
    
def stop_accelerating():
    global gravity_time, GRAVITY_ACCELERATED
    
    GRAVITY_ACCELERATED = False
    gravity_time = 450
    
def update_gravity_multiplier():
    global gravity_multiplier
    old_gravity_multiplier = gravity_multiplier
    gravity_multiplier = round(20 * (score / 100000) ** 0.7)
    print(gravity_multiplier)
    if gravity_multiplier != old_gravity_multiplier:
        tetris_song.play_level_up()
        
        
def rotate_cw():
    global current_rotation
    current_rotation = (current_rotation + 1 ) % 4
    if not is_valid_position(pieces[current_piece]["shape"][current_rotation], current_pos):
        current_rotation = (current_rotation - 1) % 4
    erase_piece((current_rotation - 1) % 4)
    draw_piece()
    
    
    
def rotate_ccw():
    global current_rotation
    current_rotation = (current_rotation - 1 ) % 4
    if not is_valid_position(pieces[current_piece]["shape"][current_rotation], current_pos):
        current_rotation = (current_rotation + 1) % 4
    erase_piece((current_rotation + 1) % 4)
    draw_piece()

def gravity_check():
    global last_fall_time
    
    now = utime.ticks_ms()
    elapsed = utime.ticks_diff(now, last_fall_time)
    
    if GRAVITY_ACCELERATED:
        gravity_time_real = 120
    else:
        gravity_time_real = gravity_time - (10 * gravity_multiplier)
    
    if elapsed > gravity_time_real:
        last_fall_time = now
        move_down()
    
def draw_board():
    color = st7789.BLACK
    for y, row in enumerate(board):
        for x, box in enumerate(row):
            if not box == -1:
                color = box
            else:
                color = st7789.BLACK
            x *= CELL_SIZE
            y_real = y * CELL_SIZE
            x += GRID_X
            y_real += GRID_Y
            d.display.fill_rect(x + 1, y_real + 1, CELL_SIZE - 2, CELL_SIZE - 2, color)

def delete_rows(rows_to_delete):
    global board, score
    
    for row in sorted(rows_to_delete, reverse=True):
        board.pop(row)
        board.insert(0, [-1] * COLS)
    draw_board()
    n = len(rows_to_delete)
    mult = 1 + (0.5 * clears_in_a_row)
    if n == 1:
        score += 100 * mult
    elif n == 2:
        score += 300 * mult
    elif n == 3:
        score += 500 * mult
    elif n == 4:
        score += 800 * mult
    
    score = round(score)
    
    if n > 0:
        tetris_song.play_line_clear()
    
    draw_score()
        
        
def check_complete_rows():
    global clears_in_a_row
    rows_to_delete = []
    
    for index, row in enumerate(board):
        if -1 not in row:
            rows_to_delete.append(index)
    if rows_to_delete:
        clears_in_a_row += 1
        delete_rows(rows_to_delete)
    else:
        clears_in_a_row = 0
    
def draw_next_piece(erase):
    
        piece = pieces[next_piece]
        h_count = piece["horizontal_count"]
        v_count = piece["vertical_count"]
        
        x = 220 + round(90/2) - round((h_count * CELL_SIZE)/2)
        y = 80 + round(80/2) - round((v_count * CELL_SIZE)/2)
        
        if not erase:
            color = piece["color"]
        else:
            color = st7789.BLACK
        
        for row, col in piece["shape"][0]:
            d.display.fill_rect(x + col * CELL_SIZE, y + row * CELL_SIZE, CELL_SIZE, CELL_SIZE, color)
      
    
    
def draw_next_piece_ui():
    d.display.rect(220, 80, 90, 80, st7789.WHITE)
    
    text_x = round(220 + (90 - (font.MAX_WIDTH * len("Next Piece"))) / 2)
    text_y = round(80 + ((80 - font.HEIGHT) / 8))
    d.display.write(font, "Next Piece", text_x, text_y, st7789.WHITE, st7789.BLACK)

        
def draw_score_ui():
    d.display.rect(5, 80, 90, 100, st7789.WHITE)
    
    text_x = round(5 + (90 - (font.MAX_WIDTH * len("Score"))) / 2)
    text_y = round(80 + ((80 - font.HEIGHT) / 8))
    d.display.write(font, "Score", text_x, text_y, st7789.WHITE, st7789.BLACK)
    
    text_x = round(5 + (90 - (font.MAX_WIDTH * len("High Score"))) / 2)
    text_y = round(120 + ((80 - font.HEIGHT) / 8))
    d.display.write(font, "High Score", text_x, text_y, st7789.WHITE, st7789.BLACK)
    
    
def draw_score():
    text_x = round(5 + (90 - (font.MAX_WIDTH * len(str(score)))) / 2)
    text_y = round(100 + ((80 - font.HEIGHT) / 8))
    d.display.write(font, str(score), text_x, text_y, st7789.WHITE, st7789.BLACK)
    update_gravity_multiplier()
  
def draw_highscore():
    highscore = storage.get_tetris_highscore()
    text_x = round(5 + (90 - (font.MAX_WIDTH * len(str(highscore)))) / 2)
    text_y = round(140 + ((80 - font.HEIGHT) / 8))
    d.display.write(font, str(highscore), text_x, text_y, st7789.WHITE, st7789.BLACK)
    


def process_input(button):
    
    
    if GAME_OVER_OPEN == True:
        if button == "S3":
            open_tetris_menu()
    
    elif GAME_STATUS == False:
        global menu_selected
        old_menu_selected = menu_selected
        if button == "UP":
            if old_menu_selected == 0:
                return
            else:
                menu_selected -= 1
                draw_selected_box(old_menu_selected, False)
                draw_selected_box(menu_selected, True)
        elif button == "DOWN":
            if old_menu_selected == (len(menu_positions) - 1):
                return
            else:
                menu_selected += 1
                draw_selected_box(old_menu_selected, False)
                draw_selected_box(menu_selected, True)
        elif button == "S3":
            open_selected()
    
    
    else:
        
        if button == "LEFT":
            move_left()
        elif button == "RIGHT":
            move_right()
        elif button == "S1":
            rotate_ccw()
        elif button == "S2":
            rotate_cw()
        elif button == "S3":
           open_tetris_menu()
        elif button == "DOWN":
            accelerate_down()
            
        

        
    

def start_game():
    global GAME_STATUS, current_piece, next_piece, score, board, clears_in_a_row, gravity_time, last_fall_time, current_pos, current_rotation, gravity_mulitplier
    board = []
    for r in range(ROWS):
        board.append([-1 for c in range(COLS)])

    
    current_piece = ""
    next_piece = ""

    current_pos = (0,3)
    current_rotation = 0

    last_fall_time = 0
    gravity_time = 450
    score = 0
    clears_in_a_row = 0
    gravity_multiplier = 1
    
    GAME_STATUS = True
    current_piece = urandom.choice(list(pieces.keys()))
    next_piece = urandom.choice(list(pieces.keys()))
    draw_grid()
    draw_next_piece_ui()
    draw_score_ui()
    draw_score()
    draw_highscore()
    draw_next_piece(False)
    draw_piece()
    tetris_song.start_music()
    
    
    