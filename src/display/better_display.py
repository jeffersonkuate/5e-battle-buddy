import math
from tkinter import *
import tkinter.scrolledtext as tkst
from threading import Thread, Lock, Event

from models.prompts import *

HORIZONTAL_PADDING = 10
VERTICAL_PADDING = 10
WINDOW_GEOMETRY = '600x800'
FOREGROUND_COLOR = 'white'
BACKGROUND_COLOR = 'black'
FONT = ('Courier', 15)


class Display(Thread):
    def __init__(self, string='', title='', finalizer=None):
        if title == '':
            title = 'Display'

        self.string = string
        self.title = title
        self.finalizer = finalizer
        self.buttons_active = False
        self.event = Event()
        self.lock = Lock()
        # self.processing_label = Label(self.window, text=PROCESSING)
        self.logs = []

        super().__init__(daemon=True)
        self.start()
        self.event.wait()
        self.event.clear()

    def run(self):
        self.window = Tk()
        self.window.title(self.title)
        self.window.configure(bg=BACKGROUND_COLOR)
        self.window.geometry(WINDOW_GEOMETRY)

        self.text_frame = tkst.Frame(master=self.window, bg=BACKGROUND_COLOR)
        self.text_box = tkst.ScrolledText(master=self.text_frame, font=FONT,
                                          bg=BACKGROUND_COLOR, fg=FOREGROUND_COLOR,
                                          width=60, height=30, wrap=WORD)
        self.buttons = ButtonSet(self.window, event=self.event)

        self.text_frame.pack(fill=BOTH, expand=YES)
        self.text_box.pack(padx=HORIZONTAL_PADDING, pady=VERTICAL_PADDING,
                           fill=BOTH, expand=True)
        self.event.set()

        self.window.mainloop()

        if self.finalizer is not None:
            self.finalizer.finalize()

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
            self.buttons.clear_buttons()
            self.string = THICK_DIVIDER + '\n' + string
            if '' != prompt:
                self.string += '\n' + THICK_SEPARATOR
                self.string += '  ' + prompt + '\n'

            for option in options:
                self.buttons.add_button(option)

            self.buttons_active = True
            self.redraw()
            value = self.buttons.harvest()

        self.processing()
        return value

    def processing(self):
        self.string += '\n\n' + THICK_DIVIDER + '\n' + PROCESSING
        self.buttons_active = False
        self.redraw()

    # Forced to have logging capabilities for compatibility,
    # but surely only a mad man would call this method... right?
    def log(self, string):
        self.logs.append('LOG:\n' + string)

    def redraw(self):
        if self.buttons_active:
            self.buttons.pack()
        else:
            self.buttons.unpack()

        self.text_box.configure(state=NORMAL)
        self.text_box.delete(1.0, END)
        self.text_box.insert(END, self.string)
        self.text_box.configure(state=DISABLED)


class ButtonSet:
    def __init__(self, window, event=None):
        self.window = window
        # We call it 'max_height' but, since we add buttons from top to bottom,
        # it's more like a starting point

        self.buttons = []
        self.result = None
        self.event = event

    def clear_buttons(self):
        for button in self.buttons:
            button.pack_forget()
        self.buttons = []

    def add_button(self, string=''):
        text = string if string is not '' else BUTTON_ENTER
        button = Button(self.window, text=text, font=FONT,
                        bg=BACKGROUND_COLOR, fg=FOREGROUND_COLOR,
                        command=(lambda: self.plant(string)))
        self.buttons.append(button)

    def pack(self):
        for button in self.buttons:
            button.pack()

    def unpack(self):
        for button in self.buttons:
            button.pack_forget()

    # Why did I name this parameter seed instead of result?
    # Probably the same reason I write comments no one will read.
    def plant(self, seed):
        self.result = seed
        if self.event is not None:
            self.event.set()

    # "It ain't much, but it's honest work"
    def harvest(self):
        if self.event is not None:
            self.event.wait()
            self.event.clear()

        result = self.result
        self.result = None
        return result
