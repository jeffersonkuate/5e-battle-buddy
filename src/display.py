import os


SEPARATOR = "====================="
DIVIDER = "||  "


class Display:
    def __init__(self, string='', response=False):
        self.string = string
        self.response = response
        self.logs = []
        self.clear = (lambda: os.system('cls')) if os.name == 'nt' else (lambda: os.system('clear'))

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

    def log(self, string):
        self.logs.append('LOG:\n' + string)

        self.clear()
        print(SEPARATOR)
        for log in self.logs:
            print(log)
            print('---')

    def redraw(self):
        self.clear()
        print(SEPARATOR)
        print(self.string)
        print(SEPARATOR)
