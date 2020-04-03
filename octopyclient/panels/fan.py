from octopyclient.utils import *
from octopyclient.common import CommonPanel, Singleton
from octopyclient.igtk import *

class FanPanel(CommonPanel, metaclass=Singleton):
    def __init__(self, ui):
        CommonPanel.__init__(self, ui)
        log.debug("FanPanel created")

        self.panelH = 2

        self.g.attach(self.createFanButton(100), 0, 0, 1, 1)
        self.g.attach(self.createFanButton(75), 1, 0, 1, 1)
        self.g.attach(self.createFanButton(50), 2, 0, 1, 1)
        self.g.attach(self.createFanButton(25), 3, 0, 1, 1)
        self.g.attach(self.createFanButton(0), 0, 1, 1, 1)

        self.arrangeButtons()

    def createFanButton(self, speed):
        if speed == 0:
            label = "Fan Off"
            image = "fan-off.svg"
        else:
            label = "{:d} %".format(speed)
            image = "fan.svg"

        return ButtonImageFromFile(label, image, self.setFanSpeed, speed)

    def setFanSpeed(self, button, speed):
        log.debug("Setting fans speed: {:d} %".format(speed))
        try:
            self.ui.printer.gcode("M106 S{:d}".format(int(255 * speed / 100)))
        except Exception as err:
            log.error("Fan speed request: {}".format(str(err)))
