import logging
from common import CommonPanel, Singleton
import igtk

class ControlPanel(CommonPanel, metaclass=Singleton):
    def __init__(self, ui, parent):
        CommonPanel.__init__(self, ui, parent)
        logging.debug("ControlPanel created")
