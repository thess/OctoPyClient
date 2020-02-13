import time

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

from octorest import OctoRest
from splash import SP
from common import BackgroundTask


def errToUser(err):
    text = err.args[0]['text']
    if "connection refused" in text:
        return "Unable to connect to Octoprint - is it running?"
    elif "request canceled" in text:
        return "Loading..."
    elif "connection broken" in text:
        return "Loading..."

    return "Unexpected error: {}".format(err)

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
    def __init__(self, host, key, width, height):
        Gtk.Window.__init__(self, title="OctoPyClient")

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

        self.sp = SP(self)
        self.bkgnd = BackgroundTask(2, self.update)

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

    def Add(self, p):
        if self.current is not None:
            self.Remove(self.current)

        self.current = p
        self.current.Show()
        self.g.attach(self.current.g, 1, 0, 1, 1)
        self.g.show_all()

    def Quit(self, p):
        if self.bkgnd is not None:
            self.bkgnd.cancel(p)
        Gtk.main_quit()

    def Remove(self, p):
        self.g.remove(p.g)
        p.Hide()

    def navHistory(self):
        self.Add(self.current.parent)

    def update(self):
        if self.connectionAttempts > 8:
            self.sp.putOnHold()
            return
        elif self.UIState == "splash":
            self.connectionAttempts += 1
        else:
            self.connectionAttempts = 0

        self.verifyConnection()

    def verifyConnection(self):
        #self.sdNotify("WATCHDOG=1")

        newUiState = "splash"
        splashMessage = "Initializing..."

        try:
            self.pState = self.Printer.state()
            print("Polled state = {}".format(self.pState))
            if self.pState == 'Operational':
                newUiState = "idle"
            elif self.pState == "Printing":
                newUiState = "printing"
            elif self.pState == "Error":
                pass
            elif self.pState == "Closed":
                print(">Attempting to connect")
                self.Printer.connect()
                newUiState = "splash"
                splashMessage = "Loading..."
            elif self.pState == "Connecting":
                    splashMessage = self.pState + "..."
        except Exception as err:
            if (time.time() - self.now) > 10:
                splashMessage = errToUser(err)

                newUiState = "splash"
                print("Unexpected error: {}", err)

        self.sp.label.set_text(splashMessage)

        if newUiState == self.UIState:
            return

        if newUiState == "idle":
                print("Printer is ready")
               #self.Add(IdleStatusPanel(self)
        elif newUiState == "printing":
                print("Printing a job")
                #i.Add(PrintStatusPanel(self)
        elif newUiState == "splash":
            self.Add(self.sp)

        self.UIState = newUiState

    def client_test(self):
        # Testing octorest
        client = make_client(self.host, self.key)
        print(get_version(client))
        print("Current state: ", client.state())
        while client.state() != 'Operational':
            print("Connecting...")
            client.connect()
            time.sleep(5)

        printer_state = client.printer()
        print('Bed temp: {:4.1f}, Extruder: {:4.1f}'.format(printer_state['temperature']['bed']['actual'],
                                                            printer_state['temperature']['tool0']['actual']))
