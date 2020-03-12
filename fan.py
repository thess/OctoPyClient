from utils import *
from common import CommonPanel, Singleton
import igtk

class FanPanel(CommonPanel, metaclass=Singleton):
    def __init__(self, ui, parent):
        CommonPanel.__init__(self, ui, parent)
        log.debug("FanPanel created")
