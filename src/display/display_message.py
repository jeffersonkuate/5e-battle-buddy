from model.prompts import *


class DisplayMessage:
    def __init__(self, display=None):
        self.display = display
        self.display_message = ""

    def add_section(self, string, level=0):
        self.add_divider(level=level)
        self.display_message += string + "\n"

    def add_text(self, string):
        self.display_message += string + "\n"

    def add_raw(self, raw):
        self.display_message += raw

    def add_divider(self, level=0):
        if level == 0:
            self.display_message += THICK_DIVIDER + "\n"
        elif level == 1:
            self.display_message += THIN_DIVIDER + "\n"
        elif level == 2:
            self.display_message += MICRO_DIVIDER + "\n"
        else:
            self.display_message += TEENY_DIVIDER + "\n"

    def print(self):
        if self.display is not None:
            self.display.print(self.display_message + THICK_DIVIDER)

    def input(self):
        if self.display is not None:
            self.display.input(self.display_message)
