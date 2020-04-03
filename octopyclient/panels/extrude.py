# Extruder / Filament functions

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from octopyclient.utils import *
from octopyclient.common import CommonPanel, Singleton, BackgroundTask
from octopyclient.igtk import *

from .temperature import TemperaturePanel

class ExtrudePanel(CommonPanel, metaclass=Singleton):
    toolData:   Gtk.Box     # Status display area
    amount:     StepButton  # Extrusion amount in mm for tool
    tool:       StepButton  # Tool selector
    labels:     {}          # Dictionary of tools and associated button images
    prevData:   {}          # Temperature data - last interval

    def __init__(self, ui):
        CommonPanel.__init__(self, ui)
        log.debug("ExtrudePanel created")
        self.panelH = 2

        self.labels = {}
        self.prevData = {}
        self.bkgnd = BackgroundTask("extruder_update", 5, self.updateTemp, ui)

        self.g.attach(self.createExtrudeButton("Extrude", "extrude", 1), 0, 0, 1, 1)
        self.g.attach(self.createExtrudeButton("Retract", "retract", -1), 3, 0, 1, 1)

        self.toolData = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.toolData.set_valign(Gtk.Align.CENTER)
        self.toolData.set_halign(Gtk.Align.CENTER)
        self.g.attach(self.toolData, 1, 0, 2, 1)

        self.amount = createStepButton("move-step.svg", [("1mm", 1), ("5mm", 5), ("10mm", 10)])
        self.g.attach(self.amount.b, 1, 1, 1, 1)
        self.g.attach(ButtonImageFromFile("Temperature", "heat-up.svg", self.showTemperature), 2, 1, 1, 1)

        self.g.attach(self.createToolButton(), 0, 1, 1, 1)

        self.arrangeButtons()


    def createExtrudeButton(self, lbl, img, direction):
        pb = createPressedButton(lbl, img+".svg", 200, self.doExtrude, direction)
        return pb.b

    def doExtrude(self, pb, dir):
        if pb.released:
            return False

        amount = dir * self.amount.steps[self.amount.idx][1]
        log.info("Filament extrude ({:s}): {:d}mm".format(self.tool.steps[self.tool.idx][0], amount))
        try:
            self.ui.printer.extrude(amount)
        except Exception as err:
            log.error("Extrude request: {}".format(str(err)))
            return False

        return True

    def showTemperature(self, source):
        self.ui.OpenPanel(TemperaturePanel(self.ui), self)

    def createToolButton(self):
        self.tool = createStepButton("extruder2.svg", [], self.changeTool)
        return self.tool.b

    def changeTool(self):
        try:
            tool = self.tool.steps[self.tool.idx][1]
            log.info("Changing tool to: {:s}".format(tool))
            self.ui.printer.tool_select(tool)
        except Exception as err:
            log.error("Tool select: {}".format(str(err)))

    def updateTemp(self):
        try:
            toolTemps = self.ui.printer.tool()
        except Exception as err:
            log.error("Getting tool temps: {}".format(str(err)))
            return

        for tool in toolTemps:
            if tool not in self.labels:
                self.addNewTool(tool)
            # Display temperature data
            self.displayTemp(tool, toolTemps[tool])
        # Save last call data for differential (see: displayTemp)
        self.prevData = toolTemps

    def addNewTool(self, name):
        log.info("Adding tool: {:s}".format(name))
        self.labels[name] = LabelWithImage("extruder2.svg", "")
        self.toolData.add(self.labels[name].b)
        addStep(self.tool, (name.capitalize(), name))

    def displayTemp(self, tool, temps):
        txt = "{:s}: {:.0f}°C ⇒ {:.0f}°C".format(tool.capitalize(), temps['actual'], temps['target'])
        if self.prevData and temps['target'] > 0:
            if self.prevData[tool]:
                txt += " ({:.1f}°C)".format(temps['actual'] - self.prevData[tool]['actual'])

        self.labels[tool].l.set_label(txt)
        self.labels[tool].b.show_all()
