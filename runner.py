#!/usr/bin/env python3

from psychopy import event, core
from psychopy.visual import Window, TextBox2
from psychopy.visual.rect import Rect
from psychopy.event import Mouse
from psychopy.core import Clock

# CONSTANTS #
# window size
WIDTH = 1920
HEIGHT = 1080

# length of experiment (in seconds)
DURATION = 25 * 60
# number of times key must be pressed to trigger effect
TRIGGER_AMTS = (100, 10, 10)
# duration of protection when triggered (in seconds)
PROTECT_DURATION = 250
# lower, upper bounds for provocation delay (in seconds)
PROVOKE_RANGE = (6, 120)
# toggles the A, B, C buttons
BTNS_ENABLED = (True, True, True)

WHITE = (1, 1, 1)
BLACK = (-1, -1, -1)
LINE_WIDTH = 2

PHASE_INTRO = 0
PHASE_CONNECT = 1
PHASE_PLAY = 2
PHASE_END = 3

STATE_INTRO = 0
STATE_SETUP = 1
STATE_INSTA = 2
STATE_INSTN = 3
STATE_INSTB = 4
STATE_INSTC = 5
STATE_START = 6

STATE_CHOOSE = 0
STATE_A = 1
STATE_B = 2
STATE_C = 3

BOX_ARGS = {
    "units": "pix",
    "lineWidth": LINE_WIDTH,
    "lineColor": BLACK
}
TEXT_ARGS = {
    "units": "pix",
    "color": BLACK,
}

HEADER_SIZE = (1800, 100)
HEADER_POS = (0, 400)
HEADER_FONTSIZE = 50

DESC1_POS = (-800, 150)
DESC2_POS = (0, 150)
DESC3_POS = (-800, -100)
DESC_FONTSIZE = 30

BTN_SIZE = (550, 50)
BACK_POS = (-500, -450)
FWD_POS = (500, -450)
BTN_FONTSIZE = 30

CONNECT_SIZE = (800, 100)
CONNECT_POS = (0, 0)
CONNECT_FONTSIZE = 30
CONNECT_DELAY = 5 # connection delay (fake)

POINTS_LABEL_POS = (-100, 250)
POINTS_COUNTER_POS = (100, 250)
BUTTON_POS = (
    (-400, 0),
    (0, 0),
    (400, 0)
)
PRESS_LABEL_POS = (-100, -250)
PRESS_COUNTER_POS = (100, -250)
LABEL_FONTSIZE = 30
COUNTER_FONTSIZE = 40
COUNTER_FONTSIZE_BIG = 50
BUTTON_FONTSIZE = 200
BUTTON_FONTSIZE_BIG = 250

# GLOBALS #
phase = PHASE_INTRO
state = STATE_INTRO

exp_clock = Clock()
protect_clock = Clock()
provoke_clock = Clock()
# track if point has been taken since the beginning or
# the last protection interval
provoked = False

# TODO: file stuff
script_file = open("script.txt", "r")
script = tuple(script_file.read().split("==="))  # split into sections
script = [string.split("---") for string in script]

fullwidth = [True, False, False, False, True, True, True]

output = open("data.csv", "w")
output.write("")

# window stuff
window = Window((WIDTH, HEIGHT), color=WHITE, fullscr=True, units="pix")

# intro stims
header_box = Rect(win=window, size=HEADER_SIZE, pos=HEADER_POS,
                  fillColor=WHITE, autoDraw=True, **BOX_ARGS)
header_text = TextBox2(win=window, pos=HEADER_POS, bold=True,
                       text="",
                       letterHeight=HEADER_FONTSIZE,
                       alignment="center", autoDraw=True,
                       **TEXT_ARGS)
# full width
desc_text1 = TextBox2(win=window, pos=DESC1_POS, bold=True,
                      text="", size=[1600, None],
                      letterHeight=DESC_FONTSIZE, anchor="top_left",
                      alignment="top_left", autoDraw=True, **TEXT_ARGS)
# right
desc_text2 = TextBox2(win=window, pos=DESC2_POS, bold=True,
                      text="",
                      letterHeight=DESC_FONTSIZE, anchor="top_left",
                      alignment="top_left", autoDraw=True, **TEXT_ARGS)
# bottom
desc_text3 = TextBox2(win=window, pos=DESC3_POS, bold=True,
                      text="", size=[1600, None],
                      letterHeight=DESC_FONTSIZE, anchor="top_left",
                      alignment="top_left", autoDraw=True, **TEXT_ARGS)
# forward/back
back_box = Rect(win=window, size=BTN_SIZE, pos=BACK_POS,
                fillColor=WHITE, autoDraw=True, **BOX_ARGS)
back_text = TextBox2(win=window, pos=BACK_POS,
                     text="Press [backspace] for previous page",
                     letterHeight=BTN_FONTSIZE,
                     alignment="center", autoDraw=True,
                     **TEXT_ARGS)
fwd_box = Rect(win=window, size=BTN_SIZE, pos=FWD_POS,
               fillColor=WHITE, autoDraw=True, **BOX_ARGS)
fwd_text = TextBox2(win=window, pos=FWD_POS,
                    text="Press [space] for next page",
                    letterHeight=BTN_FONTSIZE,
                    alignment="center", autoDraw=True,
                    **TEXT_ARGS)
intro_stims = [
    header_box,
    desc_text1,
    desc_text2,
    desc_text3,
    header_text,
    fwd_text,
    fwd_box,
    back_text,
    back_box
]

# connect stim
connect_box = Rect(win=window, size=CONNECT_SIZE, pos=CONNECT_POS,
                   fillColor=WHITE, **BOX_ARGS)
connect_text = TextBox2(win=window, pos=CONNECT_POS, bold=True,
                        text="Connecting to server . . . please wait.",
                        letterHeight=CONNECT_FONTSIZE,
                        alignment="center", autoDraw=False,
                        **TEXT_ARGS)
connect_stims = [connect_box, connect_text]
connect_start_time: float

# play stims
points_text = TextBox2(win=window, pos=POINTS_LABEL_POS,
                    text="Points:", letterHeight=LABEL_FONTSIZE,
                    alignment="center", autoDraw=False, **TEXT_ARGS)
points_counter = TextBox2(win=window, pos=POINTS_COUNTER_POS,
                    text="0", letterHeight=COUNTER_FONTSIZE,
                    alignment="center", autoDraw=False, **TEXT_ARGS)
points = 0
buttons = [TextBox2(win=window, pos=BUTTON_POS[i], text=chr(ord('A')+i),
                    letterHeight=BUTTON_FONTSIZE, alignment="center",
                    autoDraw=False, **TEXT_ARGS) for i in range(3)]
press_text = TextBox2(win=window, pos=PRESS_LABEL_POS,
                    text="Button presses:", letterHeight=LABEL_FONTSIZE,
                    alignment="center", autoDraw=False, **TEXT_ARGS)
press_counter = TextBox2(win=window, pos=PRESS_COUNTER_POS,
                    text="0", letterHeight=COUNTER_FONTSIZE,
                    alignment="center", autoDraw=False, **TEXT_ARGS)
presses = 0
play_stims = [points_text, points_counter, press_text, press_counter]

def refresh_text():
    if phase == PHASE_INTRO:
        header_text.text = script[state][0].replace("\n", "")
        if fullwidth[state]:
            desc_text1.text = script[state][1].lstrip().rstrip()
            desc_text2.text = ""
        else:
            desc_text1.text = ""
            desc_text2.text = script[state][1].lstrip().rstrip()
        desc_text3.text = script[state][2].lstrip().rstrip()


def start_connect_phase():
    global phase, state, connect_start_time
    phase = PHASE_CONNECT
    state = STATE_CHOOSE
    for stim in intro_stims:
        stim.autoDraw = False
    for stim in connect_stims:
        stim.autoDraw = True
    connect_start_time = core.monotonicClock.getTime()


def start_play_phase():
    global phase, state
    phase = PHASE_PLAY
    state = STATE_CHOOSE
    for stim in connect_stims:
        stim.autoDraw = False
    for stim in play_stims:
        stim.autoDraw = True
    for i in range(len(buttons)):
        if BTNS_ENABLED[i]:
            buttons[i].autoDraw = True


def handle_keys(keys):
    global phase, state
    if phase == PHASE_INTRO:
        if "backspace" in keys:
            # don't do anything if at the very first screen
            if state == STATE_INTRO:
                return
            # go back by 1 screen
            state -= 1
            refresh_text()
        elif "space" in keys:
            # proceed to "connect to server"
            if state == STATE_START:
                start_connect_phase()
                return
            # go forward by 1 screen
            state += 1
            refresh_text()
    elif phase == PHASE_PLAY:
        if state == STATE_CHOOSE:
            if "a" in keys:
                state = STATE_A
                presses += 1
            elif "b" in keys:
                state = STATE_B
                presses += 1
            elif "c" in keys:
                state = STATE_C
                presses += 1                


refresh_text()

# MAINLOOP #
while True:
    keys = event.getKeys()
    if "escape" in keys:
        output.close()
        core.quit()
    if phase == PHASE_INTRO:
        handle_keys(keys)
    elif phase == PHASE_CONNECT:
        if core.monotonicClock.getTime() >= connect_start_time\
                                          + CONNECT_DELAY:
            start_play_phase()
    elif phase == PHASE_PLAY:
        handle_keys(keys)

    window.flip()
