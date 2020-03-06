import logging
import threading
import time
import datetime

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from common import CommonPanel, Singleton, BackgroundTask
import igtk
import utils

DAY_SECONDS = 24 * 3600

class PrintStatusPanel(CommonPanel, metaclass=Singleton):
    pb: Gtk.ProgressBar

    def __init__(self, ui, parent):
        CommonPanel.__init__(self, ui, parent)
        logging.debug("PrintStatusPanel created")
        self.bkgnd = BackgroundTask(ui, "print_status", 1, self.update)

        self.g.attach(self.createMainBox(), 1, 0, 4, 2)
        self.arrangeButtons(False)

        self.taskRunning = threading.Lock()
        self.printerStatus = 0

    def createProgressBar(self):
        self.pb = Gtk.ProgressBar()
        self.pb.set_show_text(True)
        self.pb.set_name("PrintProg")
        return self.pb

    def createMainBox(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        box.set_valign(Gtk.Align.START)
        box.set_vexpand(True)

        grid = Gtk.Grid()
        grid.set_hexpand(True)
        grid.add(self.createInfoBox())
        grid.set_valign(Gtk.Align.START)
        grid.set_margin_top(20)

        box.add(grid)

        pb_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        pb_box.set_vexpand(True)
        pb_box.set_hexpand(True)
        pb_box.add(self.createProgressBar())

        box.add(pb_box)

        btn = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        btn.set_halign(Gtk.Align.END)
        btn.set_valign(Gtk.Align.END)
        btn.set_vexpand(True)
        btn.set_margin_top(0)
        btn.set_margin_end(0)
        btn.add(self.createPrintButton())
        btn.add(self.createPauseButton())
        btn.add(self.createStopButton())
        btn.add(igtk.ButtonImageWithSize("back.svg", self.Scaled(60), self.Scaled(60), self.ui.navHistory))

        box.add(btn)
        return box

    def createInfoBox(self):
        self.file = igtk.LabelWithImage("file2.svg", "")
        self.file.l.set_name("NameLabel")
        self.left = igtk.LabelWithImage("speed-step2.svg", "")
        self.left.l.set_name("TimeLabel")
        self.finish = igtk.LabelWithImage("finish.svg", "")
        self.finish.l.set_name("TimeLabel")
        self.bed = igtk.LabelWithImage("bed2.svg", "")
        self.bed.l.set_name("TempLabel")
        self.tool0 = igtk.LabelWithImage("extruder2.svg", "")
        self.tool0.l.set_name("TempLabel")

        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        info.set_halign(Gtk.Align.START)
        info.set_hexpand(True)
        info.set_margin_start(20)

        info.add(self.file.b)
        info.add(self.left.b)
        info.add(self.finish.b)
        info.add(self.tool0.b)
        info.add(self.bed.b)

        return info

    def createPrintButton(self):
        self.print = igtk.ButtonImageWithSize("print2.svg", self.Scaled(60), self.Scaled(60), self.doPrint)
        return self.print

    def createPauseButton(self):
        self.pause = igtk.ButtonImageWithSize("pause2.svg", self.Scaled(60), self.Scaled(60), self.doPause)
        return self.pause

    def createStopButton(self):
        self.stop = igtk.ButtonImageWithSize("stop2.svg", self.Scaled(60), self.Scaled(60), self.doStop)
        return self.stop

    def doPrint(self, source):
        try:
            logging.warning("Starting new print job")
            self.ui.printer.start()
        except Exception as err:
            logging.error(str(err))
        finally:
            self.updateTemperature()


    def doStop(self, source):
            confirmStopDialog(self, self.ui.printer)

    def doPause(self, source):
        try:
            logging.warning("Pausing/Resuming job")
            self.ui.printer.toggle()
        except Exception as err:
            logging.error(str(err))
        finally:
            self.updateTemperature()

    def update(self):
        if self.bkgnd.lock.acquire(False):
            try:
                self.updateTemperature()
                self.updateJob()
            finally:
                self.bkgnd.lock.release()

    def updateTemperature(self):
        try:
            printer_state = self.ui.printer.printer(exclude=['sd'])
        except Exception as err:
            logging.error(str(err))
            return

        self.updateState(printer_state)

        if printer_state['temperature']:
            text ="{:.0f}°C ⇒ {:.0f}°C ".format(printer_state['temperature']['bed']['actual'],
                                                printer_state['temperature']['bed']['target'])
            self.bed.l.set_label(text)
            text ="{:.0f}°C ⇒ {:.0f}°C ".format(printer_state['temperature']['tool0']['actual'],
                                                printer_state['temperature']['tool0']['target'])
            self.tool0.l.set_label(text)

    def updateState(self, printer_state):
        status = int(printer_state['state']['flags']['printing']) * 4\
                 + int(printer_state['state']['flags']['paused']) * 2\
                 + int(printer_state['state']['flags']['ready'])
        if status != self.printerStatus:
            self.printerStatus = status
            if status == 4: # Printing
                self.print.set_sensitive(False)
                self.pause.set_image(igtk.ImageFromFileWithSize("pause2.svg", self.Scaled(60), self.Scaled(60)))
                self.pause.set_sensitive(True)
                self.stop.set_sensitive(True)
                return
            elif status & 2: # Paused/Ready
                self.print.set_sensitive(False)
                self.pause.set_image(igtk.ImageFromFileWithSize("resume.svg", self.Scaled(60), self.Scaled(60)))
                self.pause.set_sensitive(True)
                self.stop.set_sensitive(True)
                return
            elif status == 1: # Ready
                self.print.set_sensitive(True)
                self.pause.set_sensitive(False)
                self.stop.set_sensitive(False)
                return
            else:
                self.print.set_sensitive(False)
                self.pause.set_sensitive(False)
                self.stop.set_sensitive(False)
                return

    def updateJob(self):
        try:
            job_state = self.ui.printer.job_info()
        except Exception as err:
            logging.error(str(err))
            return

        file = job_state['job']['file']['name']
        if file:
            file = utils.filenameEllipsis(file)
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

        finish = "-"
        if int(job_completion) == 100:
            d, s = divmod(int(job_state['job']['lastPrintTime']), DAY_SECONDS)
            text = "Completed in {}".format(datetime.timedelta(d, s))
        elif job_completion == 0:
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

            f = datetime.datetime.fromtimestamp(int(time.time()) + ptl)
            finish = "Finish time: {}".format(f.strftime("%H:%m %d-%b"))

        self.left.l.set_label(text)
        self.finish.l.set_label(finish)

def confirmStopDialog(panel, printer):
    dlg = Gtk.MessageDialog(parent=panel.ui.win,
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
            logging.warning("Stopping current job")
            printer.cancel()
    except Exception as err:
        logging.error(str(err))
    finally:
        dlg.destroy()
