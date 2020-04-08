# Printer is idle - show status

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from octopyclient.common import BackgroundTask, Singleton
from .panels.files import FilesPanel
from octopyclient.igtk import *
from .menu import *
from octopyclient.utils import *

class IdleStatusPanel(CommonPanel, metaclass=Singleton):
    def __init__(self, ui):
        CommonPanel.__init__(self, ui)
        log.debug("IdleStatusPanel created")
        self.bkgnd = BackgroundTask('temperature_update', 2, self.update, ui)
        # Specify menu buttons
        menuItems = getDefaultMenu()
        buttons = Gtk.Grid()
        buttons.set_row_homogeneous(True)
        buttons.set_column_homogeneous(True)
        self.g.attach(buttons, 2, 0, 2, 2)

        self.arrangeMenuItems(buttons, menuItems, 2)
        self.g.attach(ButtonImageStyle("Print/Files", "print2.svg", "color2", self.showFiles), 2, 2, 2, 1)

        self.showTools(self.ui)
        self.arrangeButtons()

    def showFiles(self, source):
        self.ui.OpenPanel(FilesPanel(self.ui), self)

    def update(self):
        self.updateTemperature()

    def showTools(self, ui):
        self.extruder = Tool("Extruder", "extruder2.svg", ui)
        self.bed = Tool("Bed", "bed2.svg", ui)

        g = Gtk.Grid()
        g.set_row_homogeneous(True)
        g.set_column_homogeneous(True)
        self.g.attach(g, 0, 0, 2, 3)
        g.attach(self.extruder.button, 0, 0, 2, 1)
        g.attach(self.bed.button, 0, 1, 2, 1)


    def updateTemperature(self):
        try:
            printer_state = self.ui.printer.printer(exclude=['sd', 'state'])
            if printer_state['temperature']:
                self.bed.SetTemperatures(printer_state['temperature']['bed']['actual'],
                                         printer_state['temperature']['bed']['target'])
                self.extruder.SetTemperatures(printer_state['temperature']['tool0']['actual'],
                                              printer_state['temperature']['tool0']['target'])
            else:
                self.bed.SetTemperatures(0, 0)
                self.extruder.SetTemperatures(0, 0)
        except Exception as err:
            if isRemoteDisconnect(err):
                log.debug("Ignoring remote disconnect")
                return
            log.error("Getting printer state: {}".format(str(err)))
            return


class Tool:
    isHeating:  bool
    name:       str
    button:     Gtk.Button
    image:      str

    def __init__(self, name, image, ui):
        self.name = name
        self.image = image
        self._ui = ui
        self.isHeating = False
        self.button = ButtonImageFromFile("", image, None)
        self.button.connect("clicked", self.clicked)

    def clicked(self, source):
        if self.isHeating:
            target = 0.0
        else:
            target = self.getProfileTemperature(source)

        if self.name == "Bed":
            # Bed target heatup request
            self._ui.printer.bed_target(target)
        else:
            # Extruder heatup
            self._ui.printer.tool_target(target)

    def updateStatus(self, heating):
        ctx = self.button.get_style_context()
        if heating:
            ctx.add_class("active")
        else:
            ctx.remove_class("active")

        self.isHeating = heating

    def SetTemperatures(self, actual, target):
        text = "{:.0f}°C ⇒ {:.0f}°C".format(actual, target)
        self.button.set_label(text)
        self.updateStatus(target > 0)

    def getProfileTemperature(self, source):
        temperature = 0
        try:
            settings = self._ui.printer.settings()
            profiles = settings['temperature']['profiles']
        except Exception as err:
            log.error("Get printer profiles: {}".format(str(err)))
            return temperature

        try:
            for p in profiles:
                if p['name'] == self._ui.config.preset:
                    if self.name == "Bed":
                        temperature = p['bed']
                        break
                    else:
                        temperature = p['extruder']
                        break
        except Exception as err:
            log.warning("{} profile not found: {:s}".format(self._ui.config.preset, str(err)))

        if temperature == 0:
            if self.name == "Bed":
                temperature = 60
            else:
                temperature = 210

        return temperature
