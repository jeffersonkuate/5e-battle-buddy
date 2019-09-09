import os


SEPARATOR = "====================="
DIVIDER = "||  "


class Display:
    def __init__(self, string='', response=False):
        self.string = string
        self.response = response

    def print(self, string=''):
        self.string = string
        self.redraw()

    def input(self, string='', prompt=''):
        self.string = string
        self.redraw()
        if '' != prompt:
            print(DIVIDER, end='')
            print(prompt, end="\n\n")

        return input()

    def redraw(self):
        # TODO: add Windows OS support
        os.system('clear')
        print(SEPARATOR)
        print(self.string)
        print(SEPARATOR)
