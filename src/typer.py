import pyautogui as pg


def write(text):
    for c in text:
        pg.typewrite(c)
