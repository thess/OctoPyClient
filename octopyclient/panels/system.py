import humanize
import os
import psutil

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from octopyclient.common import CommonPanel, Singleton
from octopyclient.octopyclient import __version__
from octopyclient.utils import *
from octopyclient.igtk import *

# Version info
VERSION = __version__

class SystemPanel(CommonPanel, metaclass=Singleton):
    def __init__(self, ui):
        CommonPanel.__init__(self, ui)
        log.debug("SystemPanel created")

        g = Gtk.Grid()
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

        bar.add(self.createCommandButton('restart', "restart"))
        bar.add(self.createCommandButton('reboot', "reboot2"))
        bar.add(self.createCommandButton('shutdown', "shutdown2"))
        bar.add(ButtonImageWithSize("back.svg", self.Scaled(60), self.Scaled(60), self.ui.navigateBack))

        return bar

    def createOctoPrintInfo(self):
        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        info.set_hexpand(True)
        info.set_halign(Gtk.Align.CENTER)
        info.set_vexpand(True)
        info.set_valign(Gtk.Align.CENTER)
        info.set_margin_top(25)

        logoWidth = self.Scaled(85)
        img = ImageFromFileWithSize("logo-octoprint.png", logoWidth, int(logoWidth * 1.2))
        info.add(img)

        info.add(Gtk.Label("OctoPrint Version"))
        try:
            v = self.ui.printer.version
            text = "<b>{:s} ({:s})</b>".format(v['server'], v['api'])
        except (RuntimeError, AttributeError):
            text = "<b><i>Not connected</i></b>"

        info.add(FmtLabel(text))

        try:
            with open("/etc/octopi_version") as f:
                ver = f.readline().rstrip()
            text = "OctoPi version: <b>{:s}</b>".format(ver)
        except IOError:
            text = "<i>OctoPi not installed</i>"

        info.add(FmtLabel(text))

        return info

    def createVersionInfo(self):
        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        info.set_hexpand(True)
        info.set_halign(Gtk.Align.CENTER)
        info.set_vexpand(True)
        info.set_valign(Gtk.Align.CENTER)

        if log.getEffectiveLevel() < logging.WARNING:
            logoWidth = self.Scaled(50)
            img = ImageFromFileWithSize("ks-logo.png", logoWidth, int(logoWidth * 1.5))
        else:
            img = ImageFromFileWithSize("python.png", self.Scaled(70), self.Scaled(70))
        info.add(img)
        info.add(Gtk.Label("OctoPyClient Version"))
        info.add(FmtLabel("<b>{:s}</b>".format(VERSION)))

        return info

    def createSystemInfo(self):
        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        info.set_vexpand(True)
        info.set_valign(Gtk.Align.CENTER)
        info.set_margin_bottom(10)

        title = FmtLabel("<b>System Information</b>")
        info.add(title)

        # Get VM info and Load Avg.
        vm = psutil.virtual_memory()
        info.add(FmtLabel("Memory Total / Free: <b>{:s} / {:s}</b>".format(humanize.naturalsize(vm.total),
                                                                                humanize.naturalsize(vm.free))))
        la = os.getloadavg()
        info.add(FmtLabel("Load Average: <b>{:.2f}, {:.2f}, {:.2f}</b>".format(la[0], la[1], la[2])))

        return info

    def createCommandButton(self, name, image):
        b = ButtonImageWithSize(image + ".svg", self.Scaled(60), self.Scaled(60), self.askSystemCommand)
        b.set_name(name)
        return b

    def askSystemCommand(self, source):
        name = source.get_name()
        confirmDialog(self, "Execute {:s} command?".format(name), doSystemCommand, source)

def doSystemCommand(panel, button):
    try:
        panel.ui.printer.execute_system_command('core', button.get_name())
    except Exception as err:
        log.error("Execute system command: {}".format(str(err)))
