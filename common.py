import threading
import functools
import math

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GLib
import igtk

class CommonPanel:
    panelH: int
    panelW: int

    def __init__(self, ui, parent):
        self.ui = ui
        self.parent = parent
        self.panelW = 4
        self.panelH = 2
        self.buttons = []
        self.bkgnd = None

        self.g = Gtk.Grid()
        self.g.set_row_homogeneous(True)
        self.g.set_column_homogeneous(True)

    def arrangeButtons(self):
        last = self.panelW * self.panelH
        if last < len(self.buttons):
            cols = math.ceil(float(len(self.buttons)) / float(self.panelW))
            last = int(cols) * self.panelW

        for i in range(len(self.buttons) + 1, last):
            self.addButton(Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0))

        self.back = igtk.ButtonImage("Back", "back.svg", self.ui.navHistory)
        self.addButton(self.back)

    def addButton(self, btn):
        x = int(len(self.buttons) % self.panelW)
        y = int(len(self.buttons) / self.panelW)
        self.g.attach(btn, x+1, y, 1, 1)
        self.buttons.append(btn)

    def Show(self):
        if self.bkgnd is not None:
            self.bkgnd.start()

    def Hide(self):
        if self.bkgnd is not None:
            self.bkgnd.cancel()

    def Scaled(self, val):
        return self.ui.scalef * val

class TimerTask(Thread):
    thread: threading.Timer

    def __init__(self, interval, callback):
        self.interval = interval
        self.running = False
        self.lock = threading.Lock()

        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            result = callback(*args, **kwargs)
            if result:
                self.thread = threading.Timer(self.interval, self.callback)
                self.thread.start()
            else:
                self.thread.cancel()
                self.running = False
                print("Background task failed to queue callback - exiting")

        self.callback = wrapper

class BackgroundTask(TimerTask):
    def __init__(self, interval, idleTask):
        TimerTask.__init__(self, interval, self.queueIt)
        self.idleTask = idleTask

    def queueIt(self):
        return GLib.idle_add(self.idleTask)

    def start(self, source):
        with self.lock:
            self.thread = threading.Timer(self.interval, self.callback)
            self.thread.start()
            self.running = True
            print("Background task started")
            return

    def cancel(self, source):
        with self.lock:
            if self.running:
                self.thread.cancel()
                self.running = False
                print("Background task stopped")
            return


