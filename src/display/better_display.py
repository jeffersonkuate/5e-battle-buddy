from threading import Thread, Lock, Event
from tkinter import *

from models.prompts import *

BUTTON_START_ROW = 2
BUTTON_COLUMNS = 2
WINDOW_GEOMETRY = "300x200"


class Display(Thread):
    def __init__(self, string='', response=False, title=''):
        if title == '':
            title = 'Display'

        self.string = string
        self.lock = Lock()
        self.event = Event()
        self.window = Tk()
        self.window.title(title)
        self.window.geometry(WINDOW_GEOMETRY)
        self.label = Label(self.window, text=string)
        self.label.pack()
        self.buttons = ButtonSet(self.window, event=self.event)
        self.processing_label = Label(self.window, text=PROCESSING)
        self.logs = []

        super().__init__()
        self.start()

    def run(self):
        self.window.mainloop()

    def print(self, string=''):
        with self.lock:
            self.string = string
        self.redraw()

    # TODO: account for looooooooong strings
    def input(self, string='', prompt='', options=None):
        # Empty and None check
        if not options:
            options = ['']

        with self.lock:
            self.string = THICK_DIVIDER + '\n' + string
            if '' != prompt:
                self.string += '\n' + THICK_SEPARATOR
                self.string += '  ' + prompt + '\n'

            for option in options:
                self.buttons.add_button(option)

            self.buttons.pack()


        self.redraw()

        return chr(raw)

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
    def __init__(self, window, event=None):
        self.window = window
        self.buttons = []
        self.result = None
        self.event = event

    def clear_buttons(self):
        for button in self.buttons:
            button.pack_forget()
        self.buttons = []

    def add_button(self, string):
        text = string if string is not None else BUTTON_ENTER
        self.buttons.append(Button(self.window, text=text, command=(lambda: self.plant(string))))

    def pack(self):
        pass

    # Why did I name this parameter seed instead of result?
    # Probably the same reason I write comments no one will read.
    def plant(self, seed):
        self.result = seed
        if self.event is not None:
            self.event.set()

    # "It ain't much, but it's honest work"
    def harvest(self):
        result = self.result
        self.result = None
        self.event.clear()
        return result
