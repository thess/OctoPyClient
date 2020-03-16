# Menu templates from OctoScreen

from octopyclient.common import CommonPanel
from .panels.home import HomePanel
from .panels.move import MovePanel
from .panels.extrude import ExtrudePanel
from .panels.control import ControlPanel
from .panels.fan import FanPanel
from .panels.system import SystemPanel
from .panels.temperature import TemperaturePanel
from .panels.filament import FilamentPanel

class MenuPanel(CommonPanel):
    def __init__(self, ui, parent, items):
        CommonPanel.__init__(self, ui, parent)
        self.panelH = int(1 + len(items) / 4)

        self.arrangeMenuItems(self.g, items, 4)
        self.arrangeButtons()

def getPanel(ui, parent, item):
    pname = item['panel']
    if pname == "menu":
        return MenuPanel(ui, parent, item['items'])
    elif pname == "home":
        return HomePanel(ui, parent)
    elif pname == "extrude":
        return ExtrudePanel(ui, parent)
    elif pname == "fan":
        return FanPanel(ui, parent)
    elif pname == "control":
        return ControlPanel(ui, parent)
    elif pname == "move":
        return MovePanel(ui, parent)
    elif pname == "temperature":
        return TemperaturePanel(ui, parent)
    elif pname == "filament":
        return FilamentPanel(ui, parent)
    elif pname == "system":
        return SystemPanel(ui, parent)


    return None

DEFAULT_MENU = [{'name': 'Home', 'icon': 'home2', 'panel': 'home'},
                {'name': 'Actions', 'icon': 'actions2', 'panel': 'menu', 'items':
                    [{'name': 'Move', 'icon': 'move', 'panel': 'move'},
                     {'name': 'Extrude', 'icon': 'filament', 'panel': 'extrude'},
                     {'name': 'Fan', 'icon': 'fan', 'panel': 'fan'},
                     {'name': 'Temperature', 'icon': 'heat-up', 'panel': 'temperature'},
                     {'name': 'Control', 'icon': 'control', 'panel': 'control'}]
                 },
                {'name': 'Filament', 'icon': 'filament2', 'panel': 'filament'},
                {'name': 'Configuration', 'icon': 'control2', 'panel': 'system'}]

def getDefaultMenu():
    return DEFAULT_MENU
