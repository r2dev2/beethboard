"""
In case you are wondering why this is in its own file.

Don't worry, I am wondering the same as well.
I thought I might have to deal with threads but it was actually
way simpler than that.

This file remains because I don't have access to the arduino rn
and I don't want anything to break.
"""

import pyautogui as pg


def write(text):
    for c in text:
        pg.typewrite(c)
