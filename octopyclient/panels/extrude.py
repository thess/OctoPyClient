from octopyclient.utils import *
from octopyclient.common import CommonPanel, Singleton
from octopyclient.igtk import *

class ExtrudePanel(CommonPanel, metaclass=Singleton):
    def __init__(self, ui, parent):
        CommonPanel.__init__(self, ui, parent)
        log.debug("ExtrudePanel created")
