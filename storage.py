import json
import os

def create_highscores_file():
    f = open("highscores.json", "w")
    f.write("hello")
    f.close()
    
def load_highscores():
    try:
        f = open("highscores.json", "r")
        text = f.read()
        f.close()
        highscores_dict = json.loads(text)
        return highscores_dict
    except:
        return {}
    


def save_highscore(game, score):
    highscores_dict = load_highscores()
    if highscores_dict:
        highscores_dict[game] = score
        f = open("highscores.json", "w")
        text = json.dumps(highscores_dict)
        f.write(text)
        f.close()
    
    
    
def get_tetris_highscore():
    try:
        f = open("highscores.json", "r")
        text = f.read()
        f.close()
        highscores_dict = json.loads(text)
        return highscores_dict["tetris"]
    except:
        return 0
    
    
    
    
def create_settings_file():
    f = open("settings.json", "w")
    f.write("hello")
    f.close()
    
    
def load_settings():
    try:
        f = open("settings.json", "r")
        text = f.read()
        f.close()
        settings_dict = json.loads(text)
        return settings_dict
    except:
        return {}
    
    
def retrieve_setting(setting):
    settings_dict = load_settings()
    if settings_dict:
        try:
            return settings_dict[setting]
        except:
            return 0
        
def retrieve_settings_list():
    settings_dict = load_settings()
    if settings_dict:
        return settings_dict.keys()
    return []
    


def save_setting(setting, update):
    settings_dict = load_settings()
    if settings_dict:
        settings_dict[setting] = update
        f = open("settings.json", "w")
        text = json.dumps(settings_dict)
        f.write(text)
        f.close()
        
        
        