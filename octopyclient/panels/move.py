from octopyclient.utils import *
from octopyclient.common import CommonPanel, Singleton
from octopyclient.igtk import *

class MovePanel(CommonPanel, metaclass=Singleton):
    def __init__(self, ui):
        CommonPanel.__init__(self, ui)
        log.debug("MovePanel created")
