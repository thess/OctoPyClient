from octopyclient.utils import *
from octopyclient.common import CommonPanel, Singleton
from octopyclient.igtk import *

controls = [{'name':'Motors Off', 'icon':'motor-off', 'command':'M18'},
            {'name':'Fan On', 'icon':'fan-on', 'command':'M106'},
            {'name':'Fan Off', 'icon':'fan-off', 'command':'M106 S0'}]

class ControlPanel(CommonPanel, metaclass=Singleton):
    def __init__(self, ui):
        CommonPanel.__init__(self, ui)
        log.debug("ControlPanel created")

        self.panelH = 2

        for c in controls:
            btn = self.createControlButton(c, c['icon'])
            self.addButton(btn)

        for c in self.getCustomControls():
            btn = self.createControlButton(c, "custom-script")
            self.addButton(btn)

        for c in self.getCommands():
            btn = self.createCommandButton(c, "custom-script")
            self.addButton(btn)

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
            pass

        btn = ButtonImageFromFile(strEllipsisLen(control['name'], 16), imgName+".svg", self.execCommand, control)
        return btn

    def createCommandButton(self, command, imgName):
        if 'confirm' in command:
            pass

        btn = ButtonImageFromFile(strEllipsisLen(command['name'], 16), imgName+".svg", self.execSystemCommand, command)
        return btn

    def execSystemCommand(self, source, command):
        log.info("Executing system command: {}".format(command['name']))
        try:
            self.ui.printer.execute_system_command('custom', command['action'])
        except Exception as err:
            log.error("Command {:s} failed: {}".format(command['name'], str(err)))


    def execCommand(self, source, control):
        if 'commands' in control:
            cmd = list(control['commands'])
        else:
            cmd = control['command']
        try:
            self.ui.printer.gcode(cmd)
        except Exception as err:
            log.error("Command {:s} failed: {}".format(control['name'], str(err)))

