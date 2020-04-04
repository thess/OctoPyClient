# Select pre-heat based on material type

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
            profiles = settings['temperature']['profiles']
        except Exception as err:
            log.error("Get printer profiles: {}".format(str(err)))
            return

        pcount = 0
        for profile in profiles:
            if pcount >= 10:
                log.warning("More than 10 presets. Skipping remainder.")
                break

            self.addButton(self.createProfileButton("heat-up.svg", profile))
            pcount += 1

        if pcount > 6:
            self.panelH = 3

        self.addButton(self.createProfileButton("cool-down.svg", {'name':'Cool Down', 'bed':0, 'extruder':0}))

    def createProfileButton(self, img, profile):
        btn = ButtonImageFromFile(profile['name'], img, self.doSetProfile, profile)
        return btn

    def doSetProfile(self, button, profile):
        for tool in self.tp.toolButtons:
            temp = profile['extruder']
            if tool == "bed":
                temp = profile['bed']
            # set tool target temp
            self.tp.setTarget(tool, temp)

        # return to temperature panel
        self.ui.navigateBack(button)


class TemperaturePanel(CommonPanel, metaclass=Singleton):
    tool:           StepButton    # Tool selector
    amount:         StepButton    # Temperature delta selector
    toolButtons:    {}            # Dictionary of tools and associated button image

    def __init__(self, ui):
        CommonPanel.__init__(self, ui)
        log.debug("TemperaturePanel created")
        self.panelH = 2
        self.bkgnd = BackgroundTask("tools_update", 1, self.updateToolData, ui)

        self.g.attach(self.createChangeButton("Increase", "increase.svg", 1), 0, 0, 1, 1)
        self.g.attach(self.createChangeButton("Decrease", "decrease.svg", -1), 3, 0, 1, 1)

        self.toolButtons = {}
        self.g.attach(self.createToolButton(), 0, 1, 1, 1)

        self.load = ButtonImageFromFile("Load", "extrude.svg", self.doLoadFilament)
        self.g.attach(self.load, 1, 1, 1, 1)
        self.unload = ButtonImageFromFile("Unload", "retract.svg", self.doUnloadFilament)
        self.g.attach(self.unload, 2, 1, 1, 1)

        self.amount = createStepButton("move-step.svg",
                                       [("10°C", 10.0), ("5°C", 5.0), ("1°C", 1.0)])
        self.g.attach(self.amount.b, 1, 0, 1, 1)
        self.g.attach(ButtonImageFromFile("Presets", "heat-up.svg", self.showProfile), 2, 0, 1, 1)

        self.arrangeButtons()

    def createChangeButton(self, label, image, direction):
        pb = createPressedButton(label, image, 500, self.doChangeTarget, direction)
        return pb.b

    def createToolButton(self):
        self.tool = createStepButton("", [], self.changeTool)
        return self.tool.b

    def changeTool(self):
        if self.tool.steps[self.tool.idx][1] == 'bed':
            self.load.set_sensitive(False)
            self.unload.set_sensitive(False)
            img = "bed2.svg"
        else:
            self.load.set_sensitive(True)
            self.unload.set_sensitive(True)
            img = "extruder2.svg"

        self.tool.b.set_image(ImageFromFile(img))
        self.updateToolData()

    def doChangeTarget(self, pb, direction):
        if pb.released:
            return False

        tool = self.tool.steps[self.tool.idx][1]
        target = self.getToolTarget(tool)
        if target < 0:
            return False
        target += float(direction * self.amount.steps[self.amount.idx][1])
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
            if type(err) is IndexError:
                log.error("Cannot find tool: {:s}".format(tool))
            else:
                log.error("Getting current temp: {}".format(str(err)))
            return -1
        # No temperature data
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
        self.toolButtons[name] = ButtonImageFromFile("", img, None)
        addStep(self.tool, ("", name))
        self.changeTool()

    def updateToolData(self):
        try:
            printer_state = self.ui.printer.printer(exclude=['sd', 'state'])
        except Exception as err:
            log.error("Getting current state: {}".format(str(err)))
            return

        toolTemps = printer_state['temperature']
        for tool in toolTemps:
            if tool not in self.toolButtons:
                self.addNewTool(tool)
            # Display temperature data
            txt = "{:.0f}°C ⇒ {:.0f}°C".format(toolTemps[tool]['actual'], toolTemps[tool]['target'])
            self.tool.b.set_label(txt)

    # Prusa/Marlin based firmware support M701/M702 codes
    def doLoadFilament(self):
        self.executeGCode("M701")

    def doUnloadFilament(self):
        self.executeGCode("M702")

    def executeGCode(self, cmds):
        try:
            self.ui.printer.gcode(cmds)
        except Exception as err:
            log.error("GCode rejected: {}".format(str(err)))
