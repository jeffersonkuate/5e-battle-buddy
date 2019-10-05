from threading import Thread, Lock
from tkinter import *

from models.prompts import *

TOP_BUFFER = 1
LEFT_BUFFER = 1
PAD_HEIGHT = 1000
PAD_WIDTH = 50
GEOMETRY = "300x200"


class Display(Thread):
    def __init__(self, string='', response=False, title=''):
        if title == '':
            title = 'Display'

        self.string = string
        self.lock = Lock()
        self.window = Tk()
        self.window.title(title)
        self.window.geometry(GEOMETRY)
        self.label = Label(self.window, text=string)
        self.label.pack()
        self.processing_label = Label(self.window, text=PROCESSING)
        self.buttons = []
        self.logs = []

        super().__init__()
        self.start()

    def run(self):
        self.window.mainloop()

    def print(self, string=''):
        self.string = string
        self.redraw()

    # TODO: account for looooooooong strings
    def input(self, string='', prompt='', options=None):
        with self.lock:
            self.string = THICK_DIVIDER + '\n' + string
            if '' != prompt:
                self.string += '\n' + THICK_SEPARATOR
                self.string += '  ' + prompt + '\n'

            vertical_offset = string.count('\n') + 3 + TOP_BUFFER
            raw = self.pad.getch(vertical_offset, 0)

            self.redraw()

        return chr(raw)

    def add_button(self, string):
        self.buttons.append(Button(self.window, text=string))

    def processing(self):
        self.string += '\n\n' + THICK_DIVIDER + '\n' + PROCESSING

    # Forced to have logging capabilities for compatibility,
    # but surely only a mad man would call this method... right?
    def log(self, string):
        self.logs.append('LOG:\n' + string)

    def redraw(self):
        self.screen.clear()
        i = 10
        split = self.string.split('\n')
        self.pad.addstr("stuff")
        for line in split:
            i += 1
        self.pad.refresh(0, 0, TOP_BUFFER, LEFT_BUFFER, 40, i)
        self.screen.refresh()


class ButtonSet:
    def __init__(self, window):
        self.window = window
        self.buttons = []

    def add_button(self, string):
        self.buttons.append(Button(self.window, text=string, command=(lambda: string)))
