# Menu templates from OctoScreen
from octopyclient.utils import log

from octopyclient.common import CommonPanel
from .panels.home import HomePanel
from .panels.move import MovePanel
from .panels.extrude import ExtrudePanel
from .panels.control import ControlPanel
from .panels.fan import FanPanel
from .panels.system import SystemPanel
from .panels.temperature import TemperaturePanel

class MenuPanel(CommonPanel):
    def __init__(self, ui, items):
        CommonPanel.__init__(self, ui)
        self.panelH = int(1 + len(items) / 4)

        self.arrangeMenuItems(self.g, items, 4)
        self.arrangeButtons()

def getPanel(ui, item):
    pname = item['panel']
    if pname == "menu":
        return MenuPanel(ui, item['items'])
    elif pname == "home":
        return HomePanel(ui)
    elif pname == "extrude":
        return ExtrudePanel(ui)
    elif pname == "fan":
        return FanPanel(ui)
    elif pname == "control":
        return ControlPanel(ui)
    elif pname == "move":
        return MovePanel(ui)
    elif pname == "temperature":
        return TemperaturePanel(ui)
    elif pname == "system":
        return SystemPanel(ui)

    log.critical("Panel '{}' not found".format(pname))
    return None

DEFAULT_MENU = [{'name': 'Home', 'icon': 'home2', 'panel': 'home'},
                {'name': 'Actions', 'icon': 'actions2', 'panel': 'menu', 'items':
                    [{'name': 'Move', 'icon': 'move', 'panel': 'move'},
                     {'name': 'Extrude', 'icon': 'filament', 'panel': 'extrude'},
                     {'name': 'Fan', 'icon': 'fan', 'panel': 'fan'},
                     {'name': 'Temperature', 'icon': 'heat-up', 'panel': 'temperature'},
                     {'name': 'Controls', 'icon': 'control', 'panel': 'control'}]
                 },
                {'name': 'Temperature', 'icon': 'heat-up2', 'panel': 'temperature'},
                {'name': 'System', 'icon': 'info2', 'panel': 'system'}]

def getDefaultMenu():
    return DEFAULT_MENU
