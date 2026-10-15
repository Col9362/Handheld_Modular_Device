import button
from ads1x15 import ADS1115

ads = ADS1115(button.i2c, address=0x48, gain=1)

states = {
    (0,0): "NONE",
    (0, -1): "UP",
    (0, 1): "DOWN",
    (-1, 0): "LEFT",
    (1, 0): "RIGHT",
    (-1, -1): "UP LEFT",
    (-1, 1): "DOWN LEFT",
    (1, -1): "UP RIGHT",
    (1, 1): "DOWN RIGHT",    
}

def reint_ads():
    global ads
    ads = ADS1115(button.i2c, address=0x48, gain=1)


current_state = states[(0, 0)]
DEAD_RANGE = 60

x_state = 0
y_state = 0

x_offset = 0
y_offset = 0

ratio = 0

def joystick_state():
    if button.module_present == False:
        return
    
    global current_state
    global x_state
    global y_state
    global x_offset
    global y_offset
    global ratio
    
    try:
        x = ads.read(rate=4, channel1=0)
        y = ads.read(rate=4, channel1=1)
    except Exception:
        return current_state
    
    x_norm = round(500 * ( (x-13)/(26415 - 13)))
    y_norm = round(500 * ( (y-13)/(26415 - 13)))
    
    x_offset = abs(x_norm - 255)
    y_offset = abs(y_norm - 252)
    
    if x_norm < (255 - DEAD_RANGE):
        x_state = -1
    elif x_norm > (255 + DEAD_RANGE):
        x_state = 1
    else:
        x_state = 0
        
    if y_norm < (252 - DEAD_RANGE):
        y_state = -1
    elif y_norm > (252 + DEAD_RANGE):
        y_state = 1
    else:
        y_state = 0
    
    if (x_state == 0 or y_state == 0):
        current_state = states[(x_state, y_state)]
    else:
        ratio = min(x_offset, y_offset)/max(x_offset, y_offset)
        if ratio > 0.75:
            current_state = states[(x_state, y_state)]
        else:
            if x_offset > y_offset:
                current_state = states[(x_state, 0)]
            else:
                current_state = states[(0, y_state)]
                
    return current_state
