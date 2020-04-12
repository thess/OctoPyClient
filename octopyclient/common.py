import math
import threading

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from gi.repository import GLib

from octopyclient.utils import *
from octopyclient.igtk import *

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

# Command-line config parameters
@dataclass
class Config:
    api_key:    str     # OctoPrint REST API key
    host:       str     # OctoPrint host
    port:       int     # OctoPrint server port
    width:      int     # Display size
    height:     int
    preset:     str     # Default temperature preset

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
    def __init__(self, name, interval, idleTask, ui=None):
        self.stopFlag = threading.Event()
        self.idleTask = idleTask
        self.lock = threading.Lock()
        self.interval = interval
        self.name = name
        # Add to timer thread rundown list in UI
        if ui is not None:
            ui.addRundown(self)

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
            try:
                if self.thread.isAlive():
                    self.stopFlag.set()
                    self.thread.join()
            except AttributeError:
                # Ignore timer not started errors
                pass
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

# Sub-class logger handler to supply pop-up notifications
class LogHandler(logging.Handler):
    nBox:   Gtk.Box     # Pop-up notifications
    evt:    Gtk.EventBox
    tt:     threading.Timer

    def __init__(self):
        logging.Handler.__init__(self)
        # Container
        self.nBox = Gtk.Box(Gtk.Orientation.VERTICAL, spacing=5)
        self.nBox.set_valign(Gtk.Align.START)
        self.nBox.set_halign(Gtk.Align.CENTER)
        self.nBox.set_hexpand(True)
        self.evt = None

    def handle(self, record):
        # Warnings and Errors only
        if record.levelno < logging.WARNING:
            return
        # Make sure there isn't another error showing
        while self.evt is not None:
            # pump events
            while Gtk.events_pending():
                Gtk.main_iteration()

        # WARNINGS get 4sec, ERRORS 10sec
        dpyTime = 4.0 if record.levelno == logging.WARNING else 10.0

        # Create pop-up message box label with formatted text
        lbl = FmtLabel("<b>{:s}</b>".format(record.msg))
        lbl.set_line_wrap(True)
        ctx = lbl.get_style_context()
        ctx.add_class("notification")
        ctx.add_class(record.levelname.lower())
        # Now the actual box
        self.evt = Gtk.EventBox()
        self.evt.add(lbl)
        self.evt.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.evt.connect("button-press-event", self.buttonPressed)
        # Realize popup
        self.nBox.add(self.evt)
        self.nBox.show_all()
        # Start timer thread to destroy pop-up
        self.tt = threading.Timer(dpyTime, self.buttonPressed)
        self.tt.start()

    def buttonPressed(self, parent=None, button=None):
        # Cancel timer (if necessary)
        self.tt.cancel()
        GLib.idle_add(self.evtDestroy)

    def evtDestroy(self):
        self.evt.destroy()
        self.evt = None
