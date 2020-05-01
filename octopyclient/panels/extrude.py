# Extruder / Filament functions

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from octopyclient.utils import *
from octopyclient.common import CommonPanel, Singleton, BackgroundTask
from octopyclient.igtk import *

from .temperature import TemperaturePanel, EXTRUDE_MIN_TEMP

class ExtrudePanel(CommonPanel, metaclass=Singleton):
    toolData:   Gtk.Box     # Status display area
    amount:     StepButton  # Extrusion amount in mm for tool
    tool:       StepButton  # Tool selector
    toolImages: {}          # Dictionary of tools and image labels
    ttempData:  {}          # Temperature data - last interval
    last:       str         # Last tool referenced

    def __init__(self, ui):
        CommonPanel.__init__(self, ui)
        log.debug("ExtrudePanel created")
        self.panelH = 2

        self.toolImages = {}
        self.ttempData = {}
        self.last = ''
        self.bkgnd = BackgroundTask("extruder_update", 5, self.updateTemp, ui)

        self.g.attach(self.createExtrudeButton("Extrude", "extrude", 1), 0, 0, 1, 1)
        self.g.attach(self.createExtrudeButton("Retract", "retract", -1), 3, 0, 1, 1)

        self.toolData = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.toolData.set_valign(Gtk.Align.CENTER)
        self.toolData.set_halign(Gtk.Align.CENTER)
        self.g.attach(self.toolData, 1, 0, 2, 1)

        self.amount = createStepButton("move-step.svg", [("1mm", 1), ("5mm", 5), ("10mm", 10)])
        self.g.attach(self.amount.b, 1, 1, 1, 1)
        txt = getTemperatureText(self.ui.config.width)
        self.g.attach(ButtonImageScaled(txt, "heat-up.svg", IMAGE_SIZE_NORMAL, self.showTemperature), 2, 1, 1, 1)
        self.g.attach(self.createToolButton(), 0, 1, 1, 1)

        self.arrangeButtons()

    def createExtrudeButton(self, lbl, img, direction):
        pb = createPressedButton(lbl, img+".svg", 200, self.doExtrude, direction)
        return pb.b

    def doExtrude(self, pb, dir):
        if pb.released:
            return False

        # Wait for some valid data
        if not self.ttempData:
            return True

        tool = self.tool.steps[self.tool.idx][1]
        # Cannot execute command if extruder too cool
        if self.ttempData[tool]['target'] > EXTRUDE_MIN_TEMP:
            if self.ttempData[tool]['actual'] < 0.95 * self.ttempData[tool]['target']:
                log.warning("Extruder heating, please wait")
                return False
        else:
            log.error("Extruder pre-heat required")
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
        self.tool = createStepButton("", [], self.changeTool)
        return self.tool.b

    def changeTool(self):
        tool = self.tool.steps[self.tool.idx][1]
        if tool != self.last:
            log.info("Changing tool to: {:s}".format(tool))
            self.tool.b.set_image(self.toolImages[tool][1])
            try:
                self.ui.printer.tool_select(tool)
            except Exception as err:
                log.error("Tool select: {}".format(str(err)))
            if self.last:
                self.toolImages[self.last][0].b.set_sensitive(False)
            self.toolImages[tool][0].b.set_sensitive(True)
        self.last = tool

    def updateTemp(self):
        try:
            toolTemps = self.ui.printer.tool()
        except Exception as err:
            log.error("Getting tool temps: {}".format(str(err)))
            return

        for tool in toolTemps:
            if tool not in self.toolImages:
                self.addNewTool(tool)
            # Display temperature data
            self.displayTemp(tool, toolTemps[tool])
            if self.ui.isSharedNozzle():
                break
        # Save last call data for differential (see: displayTemp)
        self.ttempData = toolTemps

    def addNewTool(self, name):
        log.info("Adding tool: {:s}".format(name))
        # Use overlay images if more than 1 extruder and not MMU
        if not self.ui.isSharedNozzle() and self.ui.getToolCount() > 1:
            imgName = name + ".svg"
            lblText = name.capitalize()
        else:
            imgName = "extruder2.svg"
            lblText = "Extruder"

        lbl = LabelWithImage(imgName, IMAGE_SIZE_ICON, "")
        self.toolData.add(lbl.b)
        lbl.b.set_sensitive(False)
        self.toolImages[name] = (lbl, ImageFromFileWithSize(imgName, displayScale(IMAGE_SIZE_NORMAL)))
        addStep(self.tool, (lblText, name))
        self.changeTool()

    def displayTemp(self, tool, temps):
        txt = "{:.0f}°C ⇒ {:.0f}°C".format(temps['actual'], temps['target'])
        if self.ttempData and temps['target'] > 0:
            if self.ttempData[tool]:
                # Display delta-temp on 2 lines if small screen
                if self.ui.config.width < 480:
                    txt += "\n\t"
                txt += " ({:.1f}°C)".format(temps['actual'] - self.ttempData[tool]['actual'])

        self.toolImages[tool][0].l.set_label(txt)
        self.toolImages[tool][0].b.show_all()
