# Splash / startup screen

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from common import CommonPanel
from system import SystemPanel
from network import NetworkPanel
import igtk


class SP(CommonPanel):
    def __init__(self, ui):
        CommonPanel.__init__(self, ui, None)

        logo = igtk.ImageFromFile("logo-octoprint.png")

        self.label = igtk.FmtLabel("...")
        self.label.set_hexpand(True)
        self.label.set_line_wrap_mode(True)
        self.label.set_max_width_chars(30)
        self.label.set_text("Initializing printer...")

        main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        main.set_valign(Gtk.Align.END)
        main.set_vexpand(True)
        main.set_hexpand(True)

        main.add(logo)
        main.add(self.label)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.add(main)
        box.add(self.createActionBar())

        self.g.add(box)

    def createActionBar(self):
        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        bar.set_halign(Gtk.Align.END)

        self.RetryButton = igtk.ButtonImageStyle("Retry", "refresh.svg", "color2", self.releaseFromHold)
        self.RetryButton.set_property("width-request", self.Scaled(80))
        self.RetryButton.set_property("visible", True)
        bar.add(self.RetryButton)
        ctx = self.RetryButton.get_style_context()
        ctx.add_class("hidden")

        sys = igtk.ButtonImageStyle("System", "info.svg", "color3", self.showSystem)
        sys.set_property("width-request", self.Scaled(80))
        bar.add(sys)

        net = igtk.ButtonImageStyle("Network", "network.svg", "color4", self.showNetwork)
        net.set_property("width-request", self.Scaled(80))
        bar.add(net)

        return bar

    def putOnHold(self):
        self.RetryButton.show()
        ctx = self.RetryButton.get_style_context()
        ctx.remove_class("hidden")
        self.label.set_text("Cannot connect to the printer. Tap \"Retry\" to try again.")

    def releaseFromHold(self, source):
        self.RetryButton.hide()
        ctx = self.RetryButton.get_style_context()
        ctx.add_class("hidden")
        self.label.set_text("Startup...")
        self.ui.connectionAttempts = 0

    def showSystem(self):
        self.ui.Add(SystemPanel(self.ui, self))

    def showNetwork(self):
        self.ui.Add(NetworkPanel(self.ui, self))
