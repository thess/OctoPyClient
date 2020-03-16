from octopyclient.utils import *
from octopyclient.common import CommonPanel, Singleton
from octopyclient.igtk import *

class HomePanel(CommonPanel, metaclass=Singleton):
    def __init__(self, ui, parent):
        CommonPanel.__init__(self, ui, parent)
        log.debug("HomePanel created")
        self.panelH = 2

        self.addButton(self.createMoveButton("Home All", "home.svg", {"x", "y", "z"}))
        self.addButton(self.createMoveButton("Home X", "home-x.svg", "x"))
        self.addButton(self.createMoveButton("Home Y", "home-y.svg", "y"))
        self.addButton(self.createMoveButton("Home Z", "home-z.svg", "z"))

        self.arrangeButtons()

    def createMoveButton(self, label, image, axes):
        return ButtonImageStyle(label, image, "color2", self.homeRequest, axes)

    def homeRequest(self, source, axes):
        log.debug("Homing {} axes".format(axes))
        self.ui.printer.home(axes)
 