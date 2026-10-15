import _thread
import utime
from machine import Pin, PWM
import settings


VOLUME = 0


buzzer = PWM(Pin(21))

NOTES = {
    "A4": 440, "B4": 494, "C5": 523, "CS5": 554, "D5": 587, "DS5": 622,
    "E5": 659, "F5": 698, "FS5": 740, "G5": 784, "GS5": 831,
    "A5": 880, "AS5": 932, "REST": 0,
}

melody = [
    ("E5",4),("B4",8),("C5",8),("D5",4),("C5",8),("B4",8),
    ("A4",4),("A4",8),("C5",8),("E5",4),("D5",8),("C5",8),
    ("B4",-4),("C5",8),("D5",4),("E5",4),
    ("C5",4),("A4",4),("A4",4),("REST",4),
    ("REST",8),("D5",4),("F5",8),("A5",4),("G5",8),("F5",8),
    ("E5",-4),("C5",8),("E5",4),("D5",8),("C5",8),
    ("B4",4),("B4",8),("C5",8),("D5",4),("E5",4),
    ("C5",4),("A4",4),("A4",4),("REST",4),
    ("E5",2),("C5",2),
    ("D5",2),("B4",2),
    ("C5",2),("A4",2),
    ("B4",1),
    ("E5",2),("C5",2),
    ("D5",2),("B4",2),
    ("C5",4),("E5",4),("A5",2),
    ("GS5",1),
]

TEMPO = 144
WHOLE_NOTE = (60000 * 4) // TEMPO

music_playing = False
music_paused = False


def update_volume(v):
    global VOLUME
    
    VOLUME = round((v / 100) * 32000)

def play_note(freq, duration_type):
    if duration_type > 0:
        note_duration = WHOLE_NOTE // duration_type
    else:
        note_duration = int((WHOLE_NOTE // abs(duration_type)) * 1.5)

    if freq == 0:
        utime.sleep_ms(note_duration)
        return

    buzzer.freq(freq)
    buzzer.duty_u16(VOLUME)
    utime.sleep_ms(int(note_duration * 0.9))
    buzzer.duty_u16(0)
    utime.sleep_ms(int(note_duration * 0.1))

def music_loop():
    global music_playing
    while music_playing:
        for note_name, duration in melody:
            if not music_playing:
                break
            while music_paused and music_playing:
                utime.sleep_ms(10)
            if not music_playing:
                break
            freq = NOTES[note_name]
            play_note(freq, duration)

def start_music():
    global music_playing
    if not music_playing:
        volume, mute = settings.retrieve_volume()
        if not mute:
            music_playing = True
            update_volume(volume)
            _thread.start_new_thread(music_loop, ())

def stop_music():
    global music_playing
    music_playing = False

def _play_effect(notes):
    global music_paused
    was_playing = music_playing
    if was_playing:
        music_paused = True
        utime.sleep_ms(15)
    for freq, dur_ms in notes:
        if freq == 0:
            utime.sleep_ms(dur_ms)
            continue
        buzzer.freq(freq)
        buzzer.duty_u16(VOLUME)
        utime.sleep_ms(dur_ms)
        buzzer.duty_u16(0)
        utime.sleep_ms(20)
    if was_playing:
        music_paused = False

def play_line_clear():
    _play_effect([(660, 60), (880, 60), (1100, 90)])

def play_level_up():
    _play_effect([(523, 80), (659, 80), (784, 80), (1047, 140)])

def play_game_over():
    stop_music()
    utime.sleep_ms(50)
    _play_effect([(392, 150), (349, 150), (330, 150), (294, 300)])
    
    