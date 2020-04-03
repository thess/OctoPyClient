from octopyclient.utils import *
from octopyclient.common import CommonPanel, Singleton
from octopyclient.igtk import *

class HomePanel(CommonPanel, metaclass=Singleton):
    def __init__(self, ui):
        CommonPanel.__init__(self, ui)
        log.debug("HomePanel created")
        self.panelH = 2

        self.addButton(self.createMoveButton("Home All", "home.svg", {"x", "y", "z"}))
        self.addButton(self.createMoveButton("Home X", "home-x.svg", "x"))
        self.addButton(self.createMoveButton("Home Y", "home-y.svg", "y"))
        self.addButton(self.createMoveButton("Home Z", "home-z.svg", "z"))

        self.arrangeButtons()

    def createMoveButton(self, label, image, axes):
        return ButtonImageFromFile(label, image, self.homeRequest, axes)

    def homeRequest(self, source, axes):
        log.debug("Homing {} axes".format(axes))
        try:
            self.ui.printer.home(axes)
        except Exception as err:
            log.error("Homing axes: {}".format(str(err)))

 