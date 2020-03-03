import time
import sdnotify
import logging

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

from octorest import OctoRest
from splash import SplashPanel
from common import BackgroundTask
from idle_status import idleStatusPanel
from print_status import PrintStatusPanel
import utils

def make_client(url, key):
    try:
        client = OctoRest(url=url, apikey=key)
        return client
    except Exception as e:
        print(e)

def get_version(client):
    message = "You are using OctoPrint v" + client.version['server']
    return message

class UI(Gtk.Window):
    _rundown = []

    def __init__(self, host, key, width, height):
        Gtk.Window.__init__(self, title="OctoPyClient")

        self.win = self
        self.host = host
        self.key = key
        self.scalef = 1.0
        self.current = None
        self.now = int(time.time())
        self.Printer = make_client(host, key)
        self.connectionAttempts = 0
        self.Settings = None
        self.UIState = None
        self.pState = None
        self.n = sdnotify.SystemdNotifier()

        self.sp = SplashPanel(self)
        self.bkgnd = BackgroundTask(self, 'status_check', 2, self.update)

        css_provider = Gtk.CssProvider()
        css_provider.load_from_path('./styles/style.css')

        screen = Gdk.Screen.get_default()
        context = Gtk.StyleContext()
        context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.set_default_size(width, height)
        self.set_resizable(False)

        self.connect('show', self.bkgnd.start)
        self.connect('destroy', self.Quit)

        o = Gtk.Overlay()
        self.add(o)

        self.g = Gtk.Grid()
        o.add(self.g)

    def OpenPanel(self, panel):
        if self.current is not None:
            self.Remove(self.current)

        self.current = panel
        self.current.Show()
        self.g.attach(self.current.g, 1, 0, 1, 1)
        self.g.show_all()

    def Quit(self, p):
        for t in self._rundown:
            t.cancel(p)
        Gtk.main_quit()

    def Remove(self, p):
        self.g.remove(p.g)
        p.Hide()

    def navHistory(self, source):
        self.OpenPanel(self.current.parent)

    def update(self):
        if self.bkgnd.lock.acquire(False):
            try:
                if self.connectionAttempts > 8:
                    self.sp.putOnHold()
                    return
                elif self.UIState == "splash":
                    self.connectionAttempts += 1
                else:
                    self.connectionAttempts = 0

                self.verifyConnection()
            finally:
                self.bkgnd.lock.release()


    def verifyConnection(self):
        self.n.notify("WATCHDOG=1")

        newUiState = "splash"
        splashMessage = "Initializing..."

        try:
            self.pState = self.Printer.state()
            logging.debug("Polled state = {}".format(self.pState))
            if self.pState == 'Operational':
                newUiState = "idle"
            elif self.pState == "Printing":
                newUiState = "printing"
            elif self.pState == "Error":
                pass
            elif self.pState == "Closed":
                logging.info("Attempting to connect")
                self.Printer.connect()
                newUiState = "splash"
                splashMessage = "Startup..."
            elif self.pState == "Connecting":
                    splashMessage = self.pState + "..."
        except Exception as err:
            if (time.time() - self.now) > 10:
                splashMessage = utils.errToUser(err)

                newUiState = "splash"
                logging.error("Unexpected error: {}", err)

        self.sp.label.set_text(splashMessage)

        if newUiState == self.UIState:
            return

        if newUiState == "idle":
                logging.info("Printer is ready")
                self.OpenPanel(idleStatusPanel(self))
        elif newUiState == "printing":
                logging.info("Printing a job")
                self.OpenPanel(PrintStatusPanel(self, self))
        elif newUiState == "splash":
            self.OpenPanel(self.sp)

        self.UIState = newUiState
