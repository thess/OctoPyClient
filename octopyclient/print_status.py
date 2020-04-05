# Show print job status with real-time updates

import time
import datetime

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from octopyclient.common import CommonPanel, Singleton, BackgroundTask
from .print_menu import PrintMenuPanel
from octopyclient.igtk import *
from octopyclient.utils import *

DAY_SECONDS = 24 * 3600

class PrintStatusPanel(CommonPanel, metaclass=Singleton):
    pb: Gtk.ProgressBar

    def __init__(self, ui):
        CommonPanel.__init__(self, ui)
        log.debug("PrintStatusPanel created")

        self.bkgnd = BackgroundTask("print_status", 1, self.update, ui)

        self.g.attach(self.createInfoBox(), 1, 0, 3, 1)
        self.g.attach(self.createProgressBar(), 1, 1, 3, 1)
        self.g.attach(self.createPauseButton(), 1, 2, 1, 1)
        self.g.attach(self.createStopButton(), 2, 2, 1, 1)
        self.g.attach(self.createMenuButton(), 3, 2, 1, 1)
        self.g.attach(self.createCompleteButton(), 1, 2, 3, 1)

        self.showTools()

        self.arrangeButtons(False)
        self.printerStatus = None


    def createProgressBar(self):
        self.pb = Gtk.ProgressBar()
        self.pb.set_show_text(True)
        self.pb.set_margin_top(10)
        self.pb.set_margin_left(10)
        self.pb.set_margin_end(self.Scaled(10))
        self.pb.set_valign(Gtk.Align.CENTER)
        self.pb.set_vexpand(True)
        self.pb.set_name("PrintProg")

        return self.pb

    def showTools(self):
        self.bed = self.createToolButton("bed2.svg")
        self.tool0 = self.createToolButton("extruder2.svg")

        self.g.attach(self.tool0, 0, 0, 1, 1)
        self.g.attach(self.bed, 0, 1, 1, 1)

    def createInfoBox(self):
        self.file = LabelWithImage("file2.svg", "")
        self.file.l.set_name("NameLabel")
        self.left = LabelWithImage("speed-step2.svg", "")
        self.left.l.set_name("TimeLabel")
        self.finish = LabelWithImage("finish.svg", "")
        self.finish.l.set_name("TimeLabel")

        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        info.set_halign(Gtk.Align.START)
        info.set_hexpand(True)
        info.set_vexpand(True)
        info.set_valign(Gtk.Align.CENTER)
        info.set_margin_left(10)
        info.set_margin_top(10)

        info.add(self.file.b)
        info.add(self.left.b)
        info.add(self.finish.b)

        return info

    def createCompleteButton(self):
        self.complete = ButtonImageWithSize("complete.svg", self.Scaled(60), self.Scaled(60), self.ui.navigateBack)
        return self.complete

    def createMenuButton(self):
        self.menu = ButtonImageWithSize("control2.svg", self.Scaled(60), self.Scaled(60), self.openPrintMenu)
        return self.menu

    def createPauseButton(self):
        self.pause = ButtonImageWithSize("pause2.svg", self.Scaled(60), self.Scaled(60), self.doPause)
        return self.pause

    def createStopButton(self):
        self.stop = ButtonImageWithSize("stop2.svg", self.Scaled(60), self.Scaled(60), self.doStop)
        return self.stop

    def createToolButton(self, img):
        b = ButtonImageFromFile("", img, None)
        ctx = b.get_style_context()
        ctx.add_class("printing-state")
        return b

    def createBedButton(self):
        b = ButtonImage("", "bed2.svg", None)
        ctx = b.get_style_context()
        ctx.add_class("printing-state")
        return b

    def openPrintMenu(self, source):
        # Force status reset on next update
        self.printerStatus = None
        self.ui.OpenPanel(PrintMenuPanel(self.ui), self)

    def doStop(self, source):
        # Skip this if cancelling
        if self.ui.pState == "Cancelling":
            log.warning("Job is cancelling")
            return
        confirmStopDialog(self, self.ui.printer)

    def doPause(self, source):
        if self.ui.pState == "Cancelling":
            log.warning("Job is cancelling")
            return
        try:
            log.warning("Pausing/Resuming job")
            self.ui.printer.toggle()
        except Exception as err:
            log.error(str(err))
        finally:
            self.updateTemperature()

    def update(self):
        self.updateTemperature()
        self.updateJob()

    def updateTemperature(self):
        try:
            printer_state = self.ui.printer.printer(exclude=['sd'])
        except Exception as err:
            if isRemoteDisconnect(err):
                log.debug("Ignoring remote disconnect")
                return
            log.error("Getting printer state: {}".format(str(err)))
            return

        self.updateState(printer_state)

        if printer_state['temperature']:
            text ="{:.0f}°C ⇒ {:.0f}°C ".format(printer_state['temperature']['bed']['actual'],
                                                printer_state['temperature']['bed']['target'])
            self.bed.set_label(text)
            text ="{:.0f}°C ⇒ {:.0f}°C ".format(printer_state['temperature']['tool0']['actual'],
                                                printer_state['temperature']['tool0']['target'])
            self.tool0.set_label(text)

    def updateState(self, printer_state):
        status = printer_state['state']['flags']
        if status != self.printerStatus:
            self.printerStatus = status
            if status['printing']:
                self.menu.set_sensitive(True)
                self.pause.set_image(ImageFromFileWithSize("pause2.svg", self.Scaled(60), self.Scaled(60)))
                self.pause.set_sensitive(True)
                self.stop.set_sensitive(True)
                self.pause.show()
                self.stop.show()
                self.menu.show()
                self.complete.hide()
                return
            elif status['paused']:
                self.menu.set_sensitive(True)
                self.pause.set_image(ImageFromFileWithSize("resume2.svg", self.Scaled(60), self.Scaled(60)))
                self.pause.set_sensitive(True)
                self.stop.set_sensitive(True)
                self.pause.show()
                self.stop.show()
                self.menu.show()
                self.complete.hide()
                return
            elif status['ready']:
                self.pause.set_sensitive(False)
                self.stop.set_sensitive(False)
                self.menu.hide()
                self.pause.hide()
                self.stop.hide()
                self.complete.show()
                return
            else:
                self.pause.set_sensitive(False)
                self.stop.set_sensitive(False)
                return

    def updateJob(self):
        try:
            job_state = self.ui.printer.job_info()
        except Exception as err:
            if isRemoteDisconnect(err):
                log.debug("Ignoring remote disconnect")
                return
            log.error("Getting job info: {}".format(str(err)))
            return

        file = job_state['job']['file']['name']
        if file:
            file = filenameEllipsis(file)
        else:
            file = "<i>File not set</i>"

        self.file.l.set_label(file)

        job_completion = job_state['progress']['completion']
        if job_completion is None:
            job_completion = 0
        self.pb.set_fraction(job_completion / 100)

        if self.ui.pState == "Operational":
            self.left.l.set_label("Printer is ready")
            self.finish.l.set_label("-")
            return
        elif self.ui.pState == 'Cancelling':
            self.left.l.set_label("Print job cancelling...")
            self.finish.l.set_label("-")
            return
        elif self.ui.pState == 'Pausing':
            self.left.l.set_label("Print job pausing...")
            self.finish.l.set_label("-")
            return

        finish = "-"
        if int(job_completion) == 100:
            d, s = divmod(int(job_state['job']['lastPrintTime']), DAY_SECONDS)
            text = "Completed in {}".format(datetime.timedelta(d, s))
        elif int(job_completion) == 0:
            text = "Warming up ..."
        else:
            d, s = divmod(int(job_state['progress']['printTime']), DAY_SECONDS)
            elapsed = datetime.timedelta(d, s)
            ptl = int(job_state['progress']['printTimeLeft'])
            text = "Elapsed: {}".format(elapsed)
            if ptl > 0:
                d, s = divmod(ptl, DAY_SECONDS)
                l = datetime.timedelta(d, s)
                text += " / Left: {}".format(l)

            now = time.time()
            f = datetime.datetime.fromtimestamp(int(now + ptl))
            finish = "Finish time: {}".format(f.strftime("%H:%M %d-%b"))

        self.left.l.set_label(text)
        self.finish.l.set_label(finish)

def confirmStopDialog(panel, printer):
    dlg = Gtk.MessageDialog(parent=panel.ui.mainwin,
                            flags=Gtk.DialogFlags.MODAL,
                            type=Gtk.MessageType.QUESTION,
                            buttons=Gtk.ButtonsType.YES_NO)
    dlg.set_markup("Stop current print job?")

    box = dlg.get_content_area()
    box.set_margin_start(15)
    box.set_margin_end(15)
    box.set_margin_top(15)
    box.set_margin_bottom(15)

    ctx = dlg.get_style_context()
    ctx.add_class("dialog")
    try:
        if dlg.run() == Gtk.ResponseType.YES:
            log.warning("Stopping current job")
            printer.cancel()
    except Exception as err:
        log.error(str(err))
    finally:
        dlg.destroy()
