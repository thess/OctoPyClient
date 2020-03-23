import math
import threading

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GLib

from octopyclient.utils import *
from octopyclient.igtk import *

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class TimerTask(threading.Timer):
    def __init__(self, name, interval, callback, event):
        threading.Timer.__init__(self, interval, callback)
        self.setName(name)
        self.interval = interval
        self.callback = callback
        self.stopped = event

    def run(self):
        while not self.stopped.wait(self.interval):
            self.callback(*self.args, **self.kwargs)
        self.stopped.clear()
        log.info("Timer thread: {:s} - exit".format(self.getName()))

class BackgroundTask():
    def __init__(self, ui, name, interval, idleTask):
        self.stopFlag = threading.Event()
        self.idleTask = idleTask
        self.lock = threading.Lock()
        self.interval = interval
        self.name = name
        # Add to timer thread rundown list in UI
        ui._rundown.append(self)

    def queueIt(self):
        return GLib.idle_add(self.idleTask)

    def start(self, source=None):
        # Invoke callback immediately. Timer queues callback after 1st interval
        GLib.idle_add(self.idleTask)

        with self.lock:
            self.thread = TimerTask(self.name, self.interval, self.queueIt, self.stopFlag)
            self.thread.start()
            log.info("Background task: {:s} - started".format(self.thread.getName()))
            return

    def cancel(self):
        with self.lock:
            if self.thread.isAlive():
                self.stopFlag.set()
                self.thread.join()
            return

class CommonPanel:
    panelH:     int
    panelW:     int
    bkgnd:      BackgroundTask
    buttons:    [Gtk.Box]
    g:          Gtk.Grid

    def __init__(self, ui):
        self.ui = ui
        # Default panel layout 4x3
        self.panelW = 4
        self.panelH = 3
        self.buttons = []
        self.bkgnd = None

        self.g = Gtk.Grid()
        self.g.set_row_homogeneous(True)
        self.g.set_column_homogeneous(True)

    def arrangeButtons(self, bAddBack=True):
        last = self.panelW * self.panelH
        if last < len(self.buttons):
            cols = math.ceil(float(len(self.buttons)) / float(self.panelW))
            last = int(cols) * self.panelW

        for i in range(len(self.buttons) + 1, last):
            self.addButton(Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0))

        if bAddBack:
            self.addButton(ButtonImageFromFile("Back", "back.svg", self.ui.navigateBack))

    def addButton(self, btn):
        x = int(len(self.buttons) % self.panelW)
        y = int(len(self.buttons) / self.panelW)
        self.g.attach(btn, x, y, 1, 1)
        self.buttons.append(btn)

    def Show(self):
        if self.bkgnd is not None:
            self.bkgnd.start()

    def Hide(self):
        if self.bkgnd is not None:
            self.bkgnd.cancel()

    def Scaled(self, val):
        return self.ui.scalef * val

    def arrangeMenuItems(self, grid, items, cols):
        from .menu import getPanel
        for i in range(len(items)):
            item = items[i]
            panel = getPanel(self.ui, item)

            if panel is not None:
                    color = "color{:d}".format((i % 4) + 1)
                    icon = "{:s}.svg".format(item['icon'])
                    row, column = divmod(i, cols)
                    grid.attach(ButtonImageStyle(item['name'], icon, color, self.addPanel, panel),
                                column, row, 1, 1)

    def addPanel(self, button, panel):
        self.ui.OpenPanel(panel, self)
