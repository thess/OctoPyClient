
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from octopyclient.common import CommonPanel, Singleton
from .panels.filament import FilamentPanel
from .panels.temperature import TemperaturePanel
from .panels.fan import FanPanel
from octopyclient.igtk import *
from octopyclient.utils import *

class PrintMenuPanel(CommonPanel, metaclass=Singleton):
    def __init__(self, ui):
        CommonPanel.__init__(self, ui)
        log.debug("PrintMenuPanel created")
        self.panelH = 2

        self.g.attach(ButtonImageStyle("Temperature", "heat-up.svg", "color4", self.showTemperature), 0, 0, 1, 1)
        self.g.attach(ButtonImageStyle("Fan", "fan.svg", "color2", self.showFan), 1, 0, 1, 1)
        self.g.attach(ButtonImageStyle("Filament", "filament.svg", "color3", self.showFilament), 2, 0, 1, 1)
        self.arrangeButtons()

    def showTemperature(self, source):
        self.ui.OpenPanel(TemperaturePanel(self.ui, self))

    def showFan(self, source):
        self.ui.OpenPanel(FanPanel(self.ui), self)

    def showFilament(self, source):
        self.ui.OpenPanel(FilamentPanel(self.ui), self)
