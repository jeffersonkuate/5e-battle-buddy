import os
import time

from models.prompts import *


# Why are you reading this, DON'T USE THIS CLASS
# (see display.better_display)
class Display:
    def __init__(self, string=''):
        self.string = string
        self.logs = []
        self.clear = (lambda: os.system('cls')) if os.name == 'nt' else (lambda: os.system('clear'))

    def print(self, string=''):
        self.string = string
        self.redraw()

    # 'options' parameter added for compatibility with BetterDisplay
    # but make no mistake, this entire class is deader than dabbing.
    def input(self, string='', prompt='', options=None):
        self.string = string
        self.redraw()
        if '' != prompt:
            print(THICK_SEPARATOR, end='')
            print(prompt, end="\n\n")

        return input()

    # Very basic/shitty logging functionality for convenience
    # Please don't actually use it... or this class in general
    def log(self, string):
        self.logs.append('LOG:\n' + string)

        self.clear()
        print(THICK_DIVIDER)
        for log in self.logs:
            print(log)
            print(THIN_DIVIDER)

    # You're still here?? bruh leave
    def redraw(self):
        self.clear()
        time.sleep(0.1)
        print(THICK_DIVIDER)
        time.sleep(0.1)
        print(self.string)
        time.sleep(0.1)
        print(THICK_DIVIDER)
