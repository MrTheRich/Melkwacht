from machine import PWM, Pin
import time
import re

notes = {"Ab":415,"A":440,"As":466,"Bb":466,"B":494,"C":523,"Cs":554,"Db":554,"D":587,"Ds":622,"Eb":622,"E":659,"F":698,"Fs":740,"Gb":740,"G":784,"Gs":831}

final_fantasy = "C.1 C.1 C.1 C.3 Ab.3 Bb.3 C.2 Bb.1 C.9"

sound_speed = 0.125 #how many seconds per eights note

loudness = 16 #between 0 and 16

sep = re.compile('\.')
buzzer = Pin(17, Pin.OUT,value = 0)

def play(tone,duration):
    global buzzer
    t = float(duration) * sound_speed
    buzzer.duty(loudness*32)
    buzzer.freq(notes[tone])
    time.sleep(t*.95)
    buzzer.duty(0)
    time.sleep(t*.05)


def play_song(song):
    global buzzer
    buzzer = PWM(Pin(5))
    buzzer.duty(0)
    melody = [tuple(sep.split(n,2)) for n in song.split(" ")]
    for note in melody:
        play(*note)
    buzzer.duty(0)
    buzzer.deinit()
    buzzer = Pin(17, Pin.OUT,value = 0)

play_song(final_fantasy)
