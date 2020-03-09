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

''' Test wapper for serializing OctoPrint API calls
class OPClient():
    opclient:   OctoRest

    def __init__(self, url, key):
        import threading
        self.xlock = threading.Lock()
        self.opclient = OctoRest(url=url, apikey=key)

    def __getattr__(self, attr):
        orig_attr = self.opclient.__getattribute__(attr)
        if callable(orig_attr):
            def hooked(*args, **kwargs):
                result = None
                try:
                    if (self.xlock.acquire(False)):
                        result = orig_attr(*args, **kwargs)
                    else:
                        logging.warning("OctoPrint overrun")
                except Exception as err:
                    logging.error(str(err))
                    raise
                finally:
                    self.xlock.release()

                return result
            return hooked
        else:
            return orig_attr
'''

def make_client(url, key):
    try:
        client = OctoRest(url=url, apikey=key)
        # client = OPClient(url, key)
        return client
    except Exception as err:
        logging.error(str(err))

def get_version(client):
    message = "You are using OctoPrint v" + client.version['server']
    return message

class UI(Gtk.Window):
    _rundown = []

    def __init__(self, host, key, width, height, style_sheet):
        Gtk.Window.__init__(self, title="OctoPyClient")

        self.win = self
        self.host = host
        self.key = key
        self.scalef = 1.0
        self.current = None
        self.now = int(time.time())
        self.printer = make_client(host, key)
        self.connectionAttempts = 0
        self.UIState = None
        self.pState = None
        # TODO: Add pop-up notifications
        self.notify = None
        self.n = sdnotify.SystemdNotifier()

        self.sp = SplashPanel(self)
        self.bkgnd = BackgroundTask(self, 'state_check', 2, self.update)

        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(style_sheet)

        screen = Gdk.Screen.get_default()
        context = Gtk.StyleContext()
        context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.set_default_size(width, height)
        self.set_resizable(False)
        # Remove window manager (optional)
        # self.set_decorated(False)

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
        self.g.attach(self.current.g, 0, 0, 1, 1)
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
        if self.connectionAttempts > 8:
            return
        elif self.UIState == "splash":
            self.connectionAttempts += 1
            if self.connectionAttempts > 8:
                self.sp.putOnHold()
        else:
            self.connectionAttempts = 0

        self.verifyConnection()

    def verifyConnection(self):
        self.n.notify("WATCHDOG=1")

        newUiState = "splash"
        splashMessage = "Initializing..."

        try:
            self.pState = self.printer.state()
            if utils.isOperational(self.pState):
                newUiState = "idle"
            elif utils.isPrinting(self.pState):
                newUiState = "printing"
            elif utils.isError(self.pState):
                pass
            elif utils.isOffline(self.pState):
                logging.info("Attempting to connect")
                self.printer.connect()
                newUiState = "splash"
                splashMessage = "Startup..."
            elif utils.isConnecting(self.pState):
                    splashMessage = self.pState + "..."
        except Exception as err:
            # After 10sec - display reason
            if (time.time() - self.now) > 10:
                splashMessage = utils.errToUser(err)

            newUiState = "splash"
            logging.error("Unexpected error: {}".format(str(err)))

        self.sp.label.set_text(splashMessage)

        if newUiState == self.UIState:
            return

        try:
            if newUiState == "idle":
                    logging.info("Printer is ready")
                    self.OpenPanel(idleStatusPanel(self))
            elif newUiState == "printing":
                    logging.info("Printing a job")
                    self.OpenPanel(PrintStatusPanel(self))
            elif newUiState == "splash":
                self.OpenPanel(self.sp)
        finally:
            self.UIState = newUiState
