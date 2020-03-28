# Select pre-heat based on material type

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from octopyclient.utils import *
from octopyclient.common import CommonPanel, Singleton, BackgroundTask
from octopyclient.igtk import *


class ProfilePanel(CommonPanel, metaclass=Singleton):
    def __init__(self, ui, tempPanel):
        CommonPanel.__init__(self, ui)
        log.debug("ProfilePanel created")
        self.tp = tempPanel
        self.panelH = 2

        self.loadProfiles()
        self.arrangeButtons()

    def loadProfiles(self):
        try:
            settings = self.ui.printer.settings()
        except Exception as err:
            log.error("Get printer settings; {}".format(str(err)))
            return

        for profile in settings['temperature']['profiles']:
            self.addButton(self.createProfileButton("heat-up.svg", profile))

        self.addButton(self.createProfileButton("cool-down.svg", {'name':'Cool Down', 'bed':0, 'extruder':0}))

    def createProfileButton(self, img, profile):
        btn = ButtonImageFromFile(profile['name'], img, self.doSetProfile, profile)
        return btn

    def doSetProfile(self, button, profile):
        for tool in self.tp.labels:
            temp = profile['extruder']
            if tool == "bed":
                temp = profile['bed']
            # set tool target temp
            self.tp.setTarget(tool, temp)

        # return to temperature panel
        self.ui.navigateBack(button)


class TemperaturePanel(CommonPanel, metaclass=Singleton):
    tool:     StepButton
    amount:   StepButton
    toolData: Gtk.Box
    labels:   {}            # Dictionary of tools and associated button image

    def __init__(self, ui):
        CommonPanel.__init__(self, ui)
        log.debug("TemperaturePanel created")
        self.panelH = 2
        self.bkgnd = BackgroundTask("tools_update", 1, self.updateToolData, ui)

        self.g.attach(self.createChangeButton("Increase", "increase.svg", 1), 0, 0, 1, 1)
        self.g.attach(self.createChangeButton("Decrease", "decrease.svg", -1), 3, 0, 1, 1)

        self.toolData = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.toolData.set_valign(Gtk.Align.CENTER)
        self.toolData.set_halign(Gtk.Align.CENTER)
        self.g.attach(self.toolData, 1, 1, 2, 1)

        self.labels = {}
        self.g.attach(self.createToolButton(), 0, 1, 1, 1)
        self.amount = createStepButton("move-step.svg",
                                       [("10°C", 10.0), ("5°C", 5.0), ("1°C", 1.0)])
        self.g.attach(self.amount.b, 1, 0, 1, 1)
        self.g.attach(ButtonImageFromFile("More", "heat-up.svg", self.showProfile), 2, 0, 1, 1)

        self.arrangeButtons()

    def createChangeButton(self, label, image, direction):
        pb = createPressedButton(label, image, 500, self.doChangeTarget, direction)
        return pb.b

    def createToolButton(self):
        self.tool = createStepButton("", [], self.changeTool)
        return self.tool.b

    def changeTool(self):
        img = "extruder2.svg"
        if self.tool.steps[self.tool.idx][1] == 'bed':
            img = "bed2.svg"

        self.tool.b.set_image(ImageFromFile(img))

    def doChangeTarget(self, pb, direction):
        if pb.released:
            return False

        tool = self.tool.steps[self.tool.idx][1]
        target = self.getToolTarget(tool) + float(direction * self.amount.steps[self.amount.idx][1])
        # Stop updating if .lt. 0
        if target < 0:
            return False
        log.info("Setting target temperature for {:s} to {:1f}".format(tool, target))
        self.setTarget(tool, target)
        return True

    def getToolTarget(self, tool):
        try:
            printer_state = self.ui.printer.printer(exclude=['sd', 'state'])
            if printer_state['temperature']:
                return printer_state['temperature'][tool]['target']
        except Exception as err:
            log.error("Getting current temp {:s}".format(tool))
            return 0

    def setTarget(self, tool, target):
        try:
            if tool == 'bed':
                self.ui.printer.bed_target(target)
            else:
                self.ui.printer.tool_target(target)
        except Exception as err:
            log.error("Setting temp for: {:s} to {:.0f} - {}".format(tool, target, str(err)))

    def showProfile(self, source):
        self.ui.OpenPanel(ProfilePanel(self.ui, self), self)

    def addNewTool(self, name):
        img = "extruder2.svg"
        if name == "bed":
            img = "bed2.svg"

        log.info("Adding tool: {:s}".format(name))

        self.labels[name] = LabelWithImage(img, "")
        self.toolData.add(self.labels[name].b)
        addStep(self.tool, (name.capitalize(), name))
        self.changeTool()

    def updateToolData(self):
        try:
            printer_state = self.ui.printer.printer(exclude=['sd', 'state'])
        except Exception as err:
            log.error("Getting current state: {}".format(str(err)))
            return

        toolTemps = printer_state['temperature']
        for tool in toolTemps:
            if tool not in self.labels:
                self.addNewTool(tool)
            # Display temperature data
            self.displayTemp(tool, toolTemps[tool])

    def displayTemp(self, tool, temps):
        txt = "{:s}: {:.0f}°C ⇒ {:.0f}°C".format(tool.capitalize(), temps['actual'], temps['target'])
        self.labels[tool].l.set_label(txt)
        self.labels[tool].b.show_all()
