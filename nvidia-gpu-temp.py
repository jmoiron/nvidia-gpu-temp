#!/usr/bin/env python3

# https://www.systutorials.com/docs/linux/man/1-mate-panel-test-applets/
# exit properly on ctrl-C
import signal

signal.signal(signal.SIGINT, signal.SIG_DFL)

import os
import sys
import logging
import subprocess

# try to turn exceptions into logging messages
def exception_handler(type, value, traceback):
    logging.exception("Uncaught exception occurred: {}".format(value))


log = logging.getLogger("nvidia-gpu-temp")
log.setLevel(logging.DEBUG)

sys.excepthook = exception_handler

# since we dont have a tty, log messages to a file so we have a chance
# to debug this thing when it doesn't work
file_handler = logging.FileHandler(os.path.expanduser("~/.nvidia-gpu-temp.log"))
file_handler.setFormatter(logging.Formatter("[%(levelname)s] %(asctime)s: %(message)s", "%Y-%m-%d %H:%M:%S"))
log.addHandler(file_handler)

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("MatePanelApplet", "4.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk
from gi.repository import MatePanelApplet
from gi.repository import Gdk
from gi.repository import GLib


def read_temperature():
    p = subprocess.run("nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader".split(), capture_output=True)
    return int(p.stdout)


def color_scale(temp):
    # roughly the colour from the nvidia X application
    if temp < 51:
        return "green"
    if temp < 70:
        return "yellow"
    return "red"


def update(label):
    temp = read_temperature()
    color = color_scale(temp)
    label.set_markup('<span color="%s">%s °C</span>' % (color, temp))
    # callback must return True to be rescheduled
    return True


def applet_fill(applet):
    log.debug("applet fill=%s", str(applet))

    # you can use this path with gio/gsettings
    # settings_path = applet.get_preferences_path()
    box = Gtk.Box()
    applet.add(box)

    temp = read_temperature()
    label = Gtk.Label(label="")
    update(label)

    box.add(label)
    applet.show_all()

    # update label every second
    GLib.timeout_add(1000, update, label)


def applet_factory(applet, iid, data):
    if iid != "NvidiaGpuTempApplet":
        return False
    applet_fill(applet)
    return True


# this sets up our applet_fill function as a loosely connected callback
# for mate-panel.  The panel itself creates the new applet, and then
# passes it into whatever service is registered to this name.
MatePanelApplet.Applet.factory_main(
    "NvidiaGpuTempAppletFactory", True, MatePanelApplet.Applet.__gtype__, applet_factory, None
)
