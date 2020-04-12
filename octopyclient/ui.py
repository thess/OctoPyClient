import time
import sdnotify

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

from octopyclient.common import BackgroundTask, LogHandler, Config
from .octorest.octorest import OctoRest
from .splash import SplashPanel
from .idle_status import IdleStatusPanel
from .print_status import PrintStatusPanel
from octopyclient.utils import *

''' Test wapper for serializing OctoPrint API calls
class OPClient():
    opclient:   OctoRest

    def __init__(self, url, key, session=None):
        import threading
        self.xlock = threading.Lock()
        self.opclient = OctoRest(url=url, apikey=key, session=session)

    def __getattr__(self, attr):
        orig_attr = self.opclient.__getattribute__(attr)
        if callable(orig_attr):
            def hooked(*args, **kwargs):
                result = None
                try:
                    if (self.xlock.acquire(False)):
                        result = orig_attr(*args, **kwargs)
                    else:
                        log.warning("OctoPrint overrun")
                except Exception as err:
                    log.error(str(err))
                    raise
                finally:
                    self.xlock.release()

                return result
            return hooked
        else:
            return orig_attr
'''

def open_client(url, key):
    try:
        # Create custom Session object with keep-alive disabled
        # Supossedly OctoPrint REST API always closes connections.
        import requests
        sess = requests.Session()
        sess.keep_alive = False
        client = OctoRest(url=url, apikey=key, session=sess)
        # client = OPClient(url, key, sess)
        return client, None
    except Exception as err:
        msg = errToUser(err)
        log.error(msg)
        return None, msg

class UI(Gtk.Window):
    _rundown = []       # Background timer threads to cancel
    _backtrack = []     # Navigation history for 'back' buttons

    _current:   Gtk.Widget  # Active panel
    _host:      str         # URL of OctoPrint server
    mainwin:    Gtk.Window  # Main UI window
    scalef:     float       # Display scale factor (480w := 1.0)
    config:     Config      # Config class struct

    def __init__(self, hostURL, cfg, style_sheet):
        Gtk.Window.__init__(self, title="OctoPyClient")

        self.mainwin = self
        self._host = hostURL
        self.config = cfg
        self.scalef = 1.5 if self.config.width > 480 else 1.0
        self._current = None
        # Navigation backup fence
        self._backtrack.append(None)
        self.now = int(time.time())
        self.printer = None
        self.connectionAttempts = 0
        self.UIState = None
        self.pState = None
        # Add pop-up notifications
        self.notify = LogHandler()
        log.addHandler(self.notify)
        # Keep systemd happy
        self.n = sdnotify.SystemdNotifier()

        self.sp = SplashPanel(self)
        self.bkgnd = BackgroundTask('state_check', 2, self.update, self)

        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(style_sheet)

        screen = Gdk.Screen.get_default()
        context = Gtk.StyleContext()
        context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.set_default_size(self.config.width, self.config.height)
        self.set_resizable(False)
        # Remove window manager (optional)
        # self.set_decorated(False)

        self.connect('show', self.bkgnd.start)
        self.connect('destroy', self.Quit)

        o = Gtk.Overlay()
        self.add(o)

        self.g = Gtk.Grid()
        o.add(self.g)
        o.add_overlay(self.notify.nBox)

    def OpenPanel(self, panel, back=None):
        if self._current is not None:
            self.Remove(self._current)
        # Push navigation 'back' context if specified
        if back is not None:
            self._backtrack.append(back)
        self._current = panel
        self._current.Show()
        self.g.attach(self._current.g, 0, 0, 1, 1)
        self.g.show_all()

    def addRundown(self, task):
        self._rundown.append(task)

    def Quit(self, source=None):
        # Kill timer threads before exit
        for t in self._rundown:
            t.cancel()
        Gtk.main_quit()

    def Remove(self, p):
        self.g.remove(p.g)
        p.Hide()

    def navigateBack(self, source):
        try:
            panel = self._backtrack.pop()
        except IndexError:
            log.error("Backup too far - reset navigation")
            panel = None

        if panel is not None:
            self.OpenPanel(panel)
        else:
            # Open default panel if top or explicit return
            self.OpenPanel(IdleStatusPanel(self))

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

        # Connect if not open yet
        if self.printer is None:
            self.printer, errMsg = open_client(self._host, self.config.api_key)

        if self.printer is not None:
            try:
                self.pState = self.printer.state()
                if isOperational(self.pState):
                    newUiState = "idle"
                    if self.UIState == "printing":
                        self.UIState = newUiState
                elif isPrinting(self.pState):
                    newUiState = "printing"
                elif isError(self.pState):
                    pass
                elif isOffline(self.pState):
                    log.info("Attempting to connect to printer")
                    self.printer.connect()
                    newUiState = "splash"
                    splashMessage = "Startup..."
                elif isConnecting(self.pState):
                    splashMessage = "Printer state: " + self.pState + "..."
            except Exception as err:
                # After 10sec - display reason
                if (int(time.time()) - self.now) > 10:
                    splashMessage = errToUser(err)
                    newUiState = "splash"
                elif not isRemoteDisconnect(err):
                    log.error("Getting printer state: {}".format(errToUser(err)))
                else:
                    log.debug("Ignoring remote disconnect")
        else:
            # Print connect retry
            splashMessage = errMsg

        self.sp.label.set_text(splashMessage)

        if newUiState == self.UIState:
            return

        try:
            if newUiState == "idle":
                    log.info("Printer is ready")
                    self.OpenPanel(IdleStatusPanel(self))
            elif newUiState == "printing":
                    log.info("Printing a job")
                    self.OpenPanel(PrintStatusPanel(self))
            elif newUiState == "splash":
                self.now = int(time.time())
                self.OpenPanel(self.sp)
        finally:
            self.UIState = newUiState
