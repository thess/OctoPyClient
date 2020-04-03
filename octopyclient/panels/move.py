# Print head move panel

from octopyclient.utils import *
from octopyclient.common import CommonPanel, Singleton
from octopyclient.igtk import *

class MovePanel(CommonPanel, metaclass=Singleton):
    step:   StepButton

    def __init__(self, ui):
        CommonPanel.__init__(self, ui)
        log.debug("MovePanel created")

        self.g.attach(self.createMoveButton("X-", "move-x-.svg", 'x', -1), 0, 1, 1, 1)
        self.g.attach(self.createMoveButton("X+", "move-x+.svg", 'x', 1), 2, 1, 1, 1)
        self.g.attach(self.createMoveButton("Y+", "move-y+.svg", 'y', 1), 1, 0, 1, 1)
        self.g.attach(self.createMoveButton("Y-", "move-y-.svg", 'y', -1), 1, 2, 1, 1)

        self.g.attach(self.createMoveButton("Z+", "move-z-.svg", 'z', 1), 3, 0, 1, 1)
        self.g.attach(self.createMoveButton("Z-", "move-z+.svg", 'z', -1), 3, 1, 1, 1)

        self.step = createStepButton("move-step.svg",
                               [("10mm", 10.0), ("1mm", 1.0), ("0.1mm", 0.1), ("0.02mm", 0.02)])

        self.g.attach(self.step.b, 2, 2, 1, 1)
        self.g.attach(self.createHomeButton(), 0, 2, 1, 1)

        self.arrangeButtons()

    def createMoveButton(self, label, image, axis, direction):
        pb = createPressedButton(label, image, 200, self.doMove, (axis, direction))
        return pb.b

    def doMove(self, pb, vect):
        # Cancel timer if released
        if pb.released:
            return False

        step_value = self.step.steps[self.step.idx][1]
        dist = float(step_value * vect[1])
        try:
            if vect[0] == 'x':
                self.ui.printer.jog(x=dist)
            elif vect[0] == 'y':
                self.ui.printer.jog(y=dist)
            elif vect[0] == 'z':
                self.ui.printer.jog(z=dist)
        except Exception as err:
            log.error("Move {}={}: {}".format(vect[0], vect[1], str(err)))
            return False

        return True


    def createHomeButton(self):
        return ButtonImage("Home All", ImageFromFile("home.svg"), self.doHomeAll)

    def doHomeAll(self, source):
        try:
            self.ui.printer.home({'x', 'y', 'z'})
        except Exception as err:
            log.error("Home all: {}".format(str(err)))
