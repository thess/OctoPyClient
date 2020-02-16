import logging
from common import CommonPanel, Singleton
import igtk

class HomePanel(CommonPanel, metaclass=Singleton):
    def __init__(self, ui, parent):
        CommonPanel.__init__(self, ui, parent)
        logging.debug("HomePanel created")

        self.addButton(self.createMoveButton("Home All", "home.svg", {"x", "y", "z"}))
        self.addButton(self.createMoveButton("Home X", "home-x.svg", "x"))
        self.addButton(self.createMoveButton("Home Y", "home-y.svg", "y"))
        self.addButton(self.createMoveButton("Home Z", "home-z.svg", "z"))

        self.arrangeButtons()

    def createMoveButton(self, label, image, axes):
        return igtk.ButtonImageStyle(label, image, "color2", self.homeRequest, axes)

    def homeRequest(self, source, axes):
        logging.info("Homing {} axes".format(axes))
        return
