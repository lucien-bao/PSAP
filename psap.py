#!/usr/bin/env python3

from psychopy import event, core
from psychopy.visual import Window, TextBox2
from psychopy.visual import ImageStim
from psychopy.visual.rect import Rect
from psychopy.core import Clock
from psychopy.clock import CountdownTimer
from random import randint
import datetime
import os

# CONSTANTS #
# window size
WIDTH = 1920
HEIGHT = 1080

# length of experiment (in seconds)
DURATION = 60 * 2  # 25 minutes
# number of times key must be pressed to trigger effect
TRIGGER_AMTS = (100, 10, 10)
# duration of protection when triggered (in seconds)
PROTECT_DURATION = 250
# lower, upper bounds for provocation delay (in seconds)
PROVOKE_RANGE = (6, 120)
# toggles the A, B, C buttons
BTNS_ENABLED = (True, True, True)
# number of rounds without participant stealing (key B) before computer steals
STEAL_PATIENCE = 5
# number of rounds without participant shielding (key C) before computer steals
SHIELD_PATIENCE = 5

WHITE = (1, 1, 1)
BLACK = (-1, -1, -1)
GREEN = (-1, 0.5, -1)
BLUE = (-1, -1, 1)
RED = (1, -1, -1)
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
CONNECT_DELAY = 5  # connection delay (fake)

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
COUNTER_FONTSIZE_BIG = 80
BUTTON_FONTSIZE = 200
BUTTON_FONTSIZE_BIG = 300

IMG_POS = (-400, 100)
IMG_SIZE = (500, 300)


def main(file_path: str=None):
    global phase, state, protect_timer, provoke_timer, provoke_active,\
        points_timer, block_timer, blocked, provoked, rounds_since_steal,\
        rounds_since_shield, script_file, script, fullwidth, participant_id,\
        date_time, output, a_presses, b_presses, c_presses, earned, deducted,\
        points, window, header_box, header_text, desc_text1, desc_text2,\
        desc_text3, back_box, back_text, fwd_box, fwd_text, img_stim,\
        intro_stims, connect_box, connect_text, connect_stims,\
        connect_start_time, points_text, points_counter, points_counter_green,\
        points_counter_red, buttons, buttons_big, press_text, press_counter,\
        presses, play_stims_start, play_stims_all, end_text
    phase = PHASE_INTRO
    state = STATE_INTRO

    exp_clock = Clock()
    protect_timer = CountdownTimer(0)
    provoke_timer = CountdownTimer(0)
    provoke_active = False  # Tracks whether the participant can be provoked
    points_timer = CountdownTimer(0)  # track time to size & color reset
    block_timer = CountdownTimer(0)  # track time to allow buttons again
    blocked = False
    # track if point has been taken since the beginning or
    # the last protection interval
    provoked = False
    rounds_since_steal = 0
    rounds_since_shield = 0

    script_file = open("script.txt", "r")
    script = tuple(script_file.read().split("==="))  # split into sections
    script = [string.split("---") for string in script]

    fullwidth = [True, False, False, False, True, True, True]

    if file_path is None:
        participant_id = input("Please enter your participant ID: ")
        date_time = datetime.datetime.now()
        date_time_str = f"{date_time.day}-{date_time.month}-" +\
        f"{date_time.year} {date_time.hour}h{date_time.minute}m{date_time.second}s"
        output = open("data" + os.sep + str(participant_id) +
                      " " + date_time_str + ".csv", "w")
    else:
        output = open(file_path, "w")
    output.write("time,a_presses,b_presses,c_presses,earned,deducted,total\n")
    a_presses = 0
    b_presses = 0
    c_presses = 0
    earned = 0
    deducted = 0
    points = 0

    # window stuff
    window = Window((WIDTH, HEIGHT), color=WHITE,
                    fullscr=True, units="pix")

    # intro stims
    header_box = Rect(win=window, size=HEADER_SIZE, pos=HEADER_POS,
                      fillColor=WHITE, autoDraw=True, **BOX_ARGS)
    header_text = TextBox2(win=window, pos=HEADER_POS, bold=True,
                           text="", color=BLACK,
                           letterHeight=HEADER_FONTSIZE,
                           alignment="center", autoDraw=True,
                           **TEXT_ARGS)
    # full width
    desc_text1 = TextBox2(win=window, pos=DESC1_POS, bold=True,
                          text="", size=[1600, None], color=BLACK,
                          letterHeight=DESC_FONTSIZE, anchor="top_left",
                          alignment="top_left", autoDraw=True, **TEXT_ARGS)
    # right
    desc_text2 = TextBox2(win=window, pos=DESC2_POS, bold=True,
                          text="", color=BLACK,
                          letterHeight=DESC_FONTSIZE, anchor="top_left",
                          alignment="top_left", autoDraw=True, **TEXT_ARGS)
    # bottom
    desc_text3 = TextBox2(win=window, pos=DESC3_POS, bold=True,
                          text="", size=[1600, None], color=BLACK,
                          letterHeight=DESC_FONTSIZE, anchor="top_left",
                          alignment="top_left", autoDraw=True, **TEXT_ARGS)
    # forward/back
    back_box = Rect(win=window, size=BTN_SIZE, pos=BACK_POS,
                    fillColor=WHITE, autoDraw=True, **BOX_ARGS)
    back_text = TextBox2(win=window, pos=BACK_POS,
                         text="Press [backspace] for previous page",
                         letterHeight=BTN_FONTSIZE,
                         alignment="center", autoDraw=True,
                         color=BLACK, **TEXT_ARGS)
    fwd_box = Rect(win=window, size=BTN_SIZE, pos=FWD_POS,
                   fillColor=WHITE, autoDraw=True, **BOX_ARGS)
    fwd_text = TextBox2(win=window, pos=FWD_POS,
                        text="Press [space] for next page",
                        letterHeight=BTN_FONTSIZE, color=BLACK,
                        alignment="center", autoDraw=True,
                        **TEXT_ARGS)

    # images
    img_stim = ImageStim(window, image="setup.png", pos=IMG_POS,
                         size=IMG_SIZE, anchor="CENTER")

    intro_stims = [
        header_box,
        desc_text1,
        desc_text2,
        desc_text3,
        header_text,
        fwd_text,
        fwd_box,
        back_text,
        back_box,
        img_stim
    ]

    # connect stim
    connect_box = Rect(win=window, size=CONNECT_SIZE, pos=CONNECT_POS,
                       fillColor=WHITE, **BOX_ARGS)
    connect_text = TextBox2(win=window, pos=CONNECT_POS, bold=True,
                            text="Connecting to server . . . please wait.",
                            letterHeight=CONNECT_FONTSIZE,
                            alignment="center", autoDraw=False,
                            color=BLACK, **TEXT_ARGS)
    connect_stims = [connect_box, connect_text]
    connect_start_time = None

    # play stims
    points_text = TextBox2(win=window, pos=POINTS_LABEL_POS,
                           text="Points:", letterHeight=LABEL_FONTSIZE,
                           alignment="center", autoDraw=False, color=BLACK,
                           **TEXT_ARGS)
    points_counter = TextBox2(win=window, pos=POINTS_COUNTER_POS,
                              text="0", letterHeight=COUNTER_FONTSIZE,
                              alignment="center", autoDraw=False, color=BLACK,
                              **TEXT_ARGS)

    points_counter_green = TextBox2(win=window, pos=POINTS_COUNTER_POS,
                                    text="0", letterHeight=COUNTER_FONTSIZE_BIG,
                                    alignment="center", autoDraw=False, color=GREEN,
                                    **TEXT_ARGS)

    points_counter_red = TextBox2(win=window, pos=POINTS_COUNTER_POS,
                                  text="0", letterHeight=COUNTER_FONTSIZE_BIG,
                                  alignment="center", autoDraw=False, color=RED,
                                  **TEXT_ARGS)

    buttons = [TextBox2(win=window, pos=BUTTON_POS[i], text=chr(ord('A')+i),
                        letterHeight=BUTTON_FONTSIZE, alignment="center",
                        autoDraw=False, color=BLACK, **TEXT_ARGS)
               for i in range(3)]
    buttons_big = [TextBox2(win=window, pos=BUTTON_POS[i], text=chr(ord('A')+i),
                            letterHeight=BUTTON_FONTSIZE_BIG, alignment="center",
                            autoDraw=False, color=BLUE, **TEXT_ARGS)
                   for i in range(3)]
    press_text = TextBox2(win=window, pos=PRESS_LABEL_POS,
                          text="Button presses:", letterHeight=LABEL_FONTSIZE,
                          alignment="center", autoDraw=False, color=BLACK,
                          **TEXT_ARGS)
    press_counter = TextBox2(win=window, pos=PRESS_COUNTER_POS,
                             text="0", letterHeight=COUNTER_FONTSIZE,
                             alignment="center", autoDraw=False, color=BLACK,
                             **TEXT_ARGS)
    presses = 0
    play_stims_start = [points_text, points_counter, press_text, press_counter]
    play_stims_all = [s for s in play_stims_start] + [points_counter_green,
                                                      points_counter_red] + [b for b in buttons] + [b for b in buttons_big]

    # end stim
    end_text = TextBox2(win=window, pos=(0, 0), bold=True,
                        text="You are now done with the experiment."
                        " Press [esc] to exit.",
                        letterHeight=CONNECT_FONTSIZE,
                        alignment="center", autoDraw=False,
                        color=BLACK, **TEXT_ARGS)


def update_log():
    output.write(",".join([
        str(core.monotonicClock.getTime()),
        str(a_presses),
        str(b_presses),
        str(c_presses),
        str(earned),
        str(deducted),
        str(points)
    ])+"\n")


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


def start_provocation():
    global provoke_timer, provoke_active
    delay = randint(PROVOKE_RANGE[0], PROVOKE_RANGE[1])
    provoke_timer = CountdownTimer(delay)
    provoke_active = True


def start_play_phase():
    global phase, state
    phase = PHASE_PLAY
    state = STATE_CHOOSE
    for stim in connect_stims:
        stim.autoDraw = False
    for stim in play_stims_start:
        stim.autoDraw = True
    for i in range(len(buttons)):
        if BTNS_ENABLED[i]:
            buttons[i].autoDraw = True

    start_provocation()


def add_press():
    global presses
    presses += 1
    press_counter.text = str(presses)


def check_trigger():
    global state, presses, points, points_timer, block_timer, blocked,\
        protect_timer, provoked, earned, rounds_since_steal,\
        rounds_since_shield
    if state == STATE_A and presses == TRIGGER_AMTS[0]:
        rounds_since_shield += 1
        rounds_since_steal += 1

        presses = 0
        press_counter.text = str(presses)
        points += 1
        earned += 1
        update_log()
        points_counter.text = str(points)
        points_counter.autoDraw = False
        points_counter_green.text = str(points)
        points_counter_green.autoDraw = True
        points_counter_red.autoDraw = False
        points_timer = CountdownTimer(1)

        for button in buttons_big:
            button.autoDraw = False

        block_timer = CountdownTimer(1)
        blocked = True
        state = STATE_CHOOSE
    elif state == STATE_B and presses == TRIGGER_AMTS[1]\
            or state == STATE_C and presses == TRIGGER_AMTS[2]:
        if state == STATE_B:
            rounds_since_steal = 0
            rounds_since_shield += 1
        else:
            rounds_since_steal += 1
            rounds_since_shield = 0

        presses = 0
        press_counter.text = str(presses)

        for button in buttons_big:
            button.autoDraw = False

        if provoked:
            protect_timer = CountdownTimer(PROTECT_DURATION)
            provoked = False

        blocked = True
        block_timer = CountdownTimer(1)
        state = STATE_CHOOSE


def handle_keys(keys):
    global phase, state, a_presses, b_presses, c_presses
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

        if state == STATE_SETUP:
            img_stim.image = "setup.png"
            img_stim.autoDraw = True
        elif state == STATE_INSTA:
            img_stim.image = "instr_a.png"
            img_stim.autoDraw = True
        elif state == STATE_INSTN:
            img_stim.image = "instr_minus.png"
            img_stim.autoDraw = True
        else:
            img_stim.autoDraw = False
    elif phase == PHASE_PLAY:
        if state == STATE_CHOOSE and not blocked:
            if "a" in keys and BTNS_ENABLED[0]:
                state = STATE_A
                for button in buttons:
                    button.autoDraw = False
                buttons_big[0].autoDraw = True
                add_press()
                a_presses += 1
            elif "b" in keys and BTNS_ENABLED[1]:
                print("b")
                state = STATE_B
                for button in buttons:
                    button.autoDraw = False
                buttons_big[1].autoDraw = True
                add_press()
                b_presses += 1
            elif "c" in keys and BTNS_ENABLED[2]:
                state = STATE_C
                for button in buttons:
                    button.autoDraw = False
                buttons_big[2].autoDraw = True
                add_press()
                c_presses += 1
        elif state == STATE_A and "a" in keys:
            add_press()
            a_presses += 1
            check_trigger()
        elif state == STATE_B and "b" in keys:
            add_press()
            b_presses += 1
            check_trigger()
        elif state == STATE_C and "c" in keys:
            add_press()
            c_presses += 1
            check_trigger()


def stop():
    output.close()
    core.quit()


def run():
    refresh_text()

    # MAINLOOP #
    while True:
        # End experiment when the timer reaches duration
        if phase == PHASE_PLAY and core.monotonicClock.getTime() > DURATION:
            phase = PHASE_END
            for stim in play_stims_all:
                stim.autoDraw = False
            end_text.autoDraw = True

        # Reset from green points counter after point scored
        if phase == PHASE_PLAY and points_timer.getTime() < 0:
            points_counter.autoDraw = True
            points_counter_green.autoDraw = False
            points_counter_red.autoDraw = False
        # Bring back buttons after completion of A, B, C actions
        if phase == PHASE_PLAY and blocked and block_timer.getTime() < 0:
            for button in buttons:
                button.autoDraw = True
            blocked = False
        # Make sure participant is interacting with point-stealing/protecting
        if phase == PHASE_PLAY and\
                (rounds_since_shield > 5 or rounds_since_steal > 5):
            provoke_timer.reset(0)
            rounds_since_steal = rounds_since_shield = 0
        # Trigger provocation
        if phase == PHASE_PLAY and provoke_active and provoke_timer.getTime() < 0:
            # If a protection interval is up, the point-taking interaction is
            # skipped. A new provocation event and delay are generated whether
            # there is a protection interval up or not.
            if protect_timer.getTime() < 0:
                points_counter.autoDraw = False
                points -= 1
                deducted += 1
                update_log()
                points_counter.text = str(points)
                points_counter_red.text = str(points)
                points_counter_red.autoDraw = True
                points_timer = CountdownTimer(1)
                provoked = True
            start_provocation()

        keys = event.getKeys()
        if "escape" in keys or core.monotonicClock.getTime() > DURATION:
            stop()
        if phase == PHASE_INTRO:
            handle_keys(keys)
        elif phase == PHASE_CONNECT:
            if core.monotonicClock.getTime() >= connect_start_time\
                    + CONNECT_DELAY:
                start_play_phase()
        elif phase == PHASE_PLAY:
            handle_keys(keys)

        window.flip()


if __name__ == "__main__":
    main()
