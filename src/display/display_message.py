from model.prompts import *


class DisplayMessage:
    def __init__(self, display):
        self.display = display
        self.display_message = ""

    def add_section(self, string):
        self.add_divider()
        self.display_message += string + "\n"

    def add_sub_section(self, string):
        self.add_sub_divider()
        self.display_message += string + "\n"

    def add_text(self, string):
        self.display_message += string + "\n"

    def add_raw(self, raw):
        self.display_message += raw

    def add_divider(self):
        self.display_message += THICK_DIVIDER + "\n"

    def add_sub_divider(self):
        self.display_message += THIN_DIVIDER + "\n"

    def print(self):
        self.display.print(self.display_message + THICK_DIVIDER)

    def input(self):
        self.display.input(self.display_message)
