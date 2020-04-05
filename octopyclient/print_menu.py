# Controls available when printing

from octopyclient.common import CommonPanel, Singleton
from .panels.extrude import ExtrudePanel
from .panels.temperature import TemperaturePanel
from .panels.fan import FanPanel
from .panels.move import MovePanel

from octopyclient.igtk import *
from octopyclient.utils import *

class PrintMenuPanel(CommonPanel, metaclass=Singleton):
    frb:        StepButton  # Flow-rate factor (75 .. 125)

    def __init__(self, ui):
        CommonPanel.__init__(self, ui)
        log.debug("PrintMenuPanel created")
        self.panelH = 2

        self.g.attach(ButtonImageStyle("Fan", "fan.svg", "color2", self.showFan), 0, 0, 1, 1)
        self.frb = createStepButton("speed-step.svg",
                                    [("Slow", 75), ("Normal", 100), ("Fast", 125)], self.changeFlowrate)
        ctx = self.frb.b.get_style_context()
        ctx.add_class("color1")

        self.g.attach(self.frb.b, 1, 0, 1, 1)
        self.g.attach(ButtonImageStyle("Temperature", "heat-up.svg", "color4", self.showTemperature), 2, 0, 1, 1)
        self.g.attach(ButtonImageStyle("Extrude", "filament.svg", "color3", self.showExtrude), 3, 0, 1, 1)
        self.g.attach(ButtonImageStyle("Move", "move.svg", "color4", self.showMove), 0, 1, 1, 1)

        self.arrangeButtons()

    def showTemperature(self, source):
        self.ui.OpenPanel(TemperaturePanel(self.ui), self)

    def showFan(self, source):
        self.ui.OpenPanel(FanPanel(self.ui), self)

    def showExtrude(self, source):
        self.ui.OpenPanel(ExtrudePanel(self.ui), self)

    def showMove(self, source):
        self.ui.OpenPanel(MovePanel(self.ui), self)

    def changeFlowrate(self):
        try:
            factor = self.frb.steps[self.frb.idx][1]
            log.info("Changing flowrate to: {:d}%".format(factor))
            self.ui.printer.flowrate(factor)
        except Exception as err:
            log.error("Setting flowrate: {}".format(str(err)))
