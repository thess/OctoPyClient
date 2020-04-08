# Misc control functions and OctoPrint user defined commands and controls

from octopyclient.common import CommonPanel, Singleton
from octopyclient.utils import *
from octopyclient.igtk import *

controls = [{'name':'Motors Off', 'icon':'motor-off', 'command':'M18'},
            {'name':'Fan On', 'icon':'fan-on', 'command':'M106'},
            {'name':'Fan Off', 'icon':'fan-off', 'command':'M106 S0'}]

class ControlPanel(CommonPanel, metaclass=Singleton):
    def __init__(self, ui):
        CommonPanel.__init__(self, ui)
        log.debug("ControlPanel created")
        # Default to 2 rows of buttons
        self.panelH = 2
        cCount = 0

        for c in controls:
            btn = self.createControlButton(c, c['icon'])
            self.addButton(btn)
            cCount += 1

        for c in self.getCustomControls():
            if cCount >= 11:
                log.warning("More than 11 commands. Skipping...")
                break
            btn = self.createControlButton(c, "custom-script")
            self.addButton(btn)
            cCount += 1

        for c in self.getCommands():
            if cCount >= 10:
                log.warning("More than 11 commands. Skipping...")
                break
            btn = self.createCommandButton(c, "custom-script")
            self.addButton(btn)
            cCount += 1

        if cCount > 7:
            self.panelH = 3

        self.arrangeButtons()

    def getCustomControls(self):
        log.info("Retrieving custom controls")
        try:
            controls = self.ui.printer.custom_control_request()
        except Exception as err:
            log.error("Get custom controls: {}".format(str(err)))
            return []

        control = []
        for c in controls:
            if 'children' in c:
                for cc in c['children']:
                    if 'command' in cc or 'script' in cc:
                        control.append(cc)

        return control

    def getCommands(self):
        log.info("Retrieving custom commands")
        try:
            commands = self.ui.printer.system_commands()
        except Exception as err:
            log.error("Get custom commands: {}".format(str(err)))
            return []

        return commands['custom']

    def createControlButton(self, control, imgName):
        if 'confirm' in control:
            cb = self.askCommand
        else:
            cb = self.execCommand

        btn = ButtonImageFromFile(strEllipsisLen(control['name'], int(self.Scaled(12))),
                                  imgName+".svg", cb, control)
        return btn

    def createCommandButton(self, command, imgName):
        if 'confirm' in command:
            cb = self.askSystemCommand
        else:
            cb = self.execSystemCommand

        btn = ButtonImageFromFile(strEllipsisLen(command['name'], int(self.Scaled(12))),
                                  imgName+".svg", cb, command)
        return btn

    def askSystemCommand(self, source, cmd):
        confirmDialog(self, fixupHTML(cmd['confirm']), self.execSystemCommand, cmd)

    def execSystemCommand(self, source, command):
        log.info("Executing system command: {}".format(command['name']))
        try:
            self.ui.printer.execute_system_command('custom', command['action'])
        except Exception as err:
            log.error("Command {:s} failed: {}".format(command['name'], str(err)))

    def askCommand(self, source, cmd):
        confirmDialog(self, fixupHTML(cmd['confirm']), self.execCommand, cmd)

    def execCommand(self, source, control):
        log.info("Executing command: {}".format(control['name']))
        if 'commands' in control:
            cmd = list(control['commands'])
        else:
            cmd = control['command']
        try:
            self.ui.printer.gcode(cmd)
        except Exception as err:
            log.error("Command {:s} failed: {}".format(control['name'], str(err)))

