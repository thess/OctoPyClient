import humanize
import os
import psutil
from utils import *

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from common import CommonPanel, Singleton
import igtk

# Version info
VERSION = "0.4.1"

class SystemPanel(CommonPanel, metaclass=Singleton):
    def __init__(self, ui, parent):
        CommonPanel.__init__(self, ui, parent)
        log.debug("SystemPanel created")

        g = Gtk.Grid()
        g.set_row_homogeneous(True)
        g.set_column_homogeneous(True)

        g.attach(self.createOctoPrintInfo(), 0, 0, 2, 1)
        g.attach(self.createVersionInfo(), 2, 0, 2, 1)
        g.attach(self.createSystemInfo(), 0, 1, 4, 1)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.add(g)
        box.add(self.createActionBar())

        self.g.add(box)

    def createActionBar(self):
        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        bar.set_halign(Gtk.Align.END)

        # bar.add(self.createCommandButton("restart", self.doRestart))
        # bar.add(self.createCommandButton("reboot", self.doReboot))
        # bar.add(self.createCommandBuggon("shutdown", self.doShutdown))
        bar.add(igtk.ButtonImageWithSize("back.svg", self.Scaled(35), self.Scaled(35), self.ui.navHistory))

        return bar

    def createOctoPrintInfo(self):
        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        info.set_hexpand(True)
        info.set_halign(Gtk.Align.CENTER)
        info.set_vexpand(True)
        info.set_valign(Gtk.Align.CENTER)

        logoWidth = self.Scaled(85)
        img = igtk.ImageFromFileWithSize("logo-octoprint.png", logoWidth, int(logoWidth * 1.2))
        info.add(img)

        info.add(Gtk.Label("OctoPrint Version"))
        try:
            v = self.ui.printer.version
            text = "<b>{:s} ({:s})</b>".format(v['server'], v['api'])
        except:
            text = "<b><i>Not connected</i></b>"

        info.add(igtk.FmtLabel(text))

        return info

    def createVersionInfo(self):
        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        info.set_hexpand(True)
        info.set_halign(Gtk.Align.CENTER)
        info.set_vexpand(True)
        info.set_valign(Gtk.Align.CENTER)

        if log.root.level < logging.WARNING:
            logoWidth = self.Scaled(50)
            img = igtk.ImageFromFileWithSize("ks-logo.png", logoWidth, int(logoWidth * 1.5))
        else:
            img = igtk.ImageFromFileWithSize("python.png", self.Scaled(70), self.Scaled(70))
        info.add(img)
        info.add(Gtk.Label("OctoPyClient Version"))
        info.add(igtk.FmtLabel("<b>{:s}</b>".format(VERSION)))

        return info

    def createSystemInfo(self):
        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        info.set_vexpand(True)
        info.set_valign(Gtk.Align.CENTER)

        title = igtk.FmtLabel("<b>System Information</b>")
        title.set_margin_bottom(5)
        title.set_margin_top(15)
        info.add(title)

        # Get VM info and Load Avg.
        vm = psutil.virtual_memory()
        info.add(igtk.FmtLabel("Memory Total / Free: <b>{:s} / {:s}</b>".format(humanize.naturalsize(vm.total),
                                                                                humanize.naturalsize(vm.free))))
        la = os.getloadavg()
        info.add(igtk.FmtLabel("Load Average: <b>{:.2f}, {:.2f}, {:.2f}</b>".format(la[0], la[1], la[2])))

        return info

