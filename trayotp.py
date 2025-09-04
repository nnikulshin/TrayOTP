#!/usr/bin/python
import os
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, AyatanaAppIndicator3 as tray
import pyotp
from functools import partial

def quit(_):
  Gtk.main_quit()

cboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
otps = []
menu = Gtk.Menu()

try:
  file = open(os.path.expanduser("~/.local/share/trayotp.dat"), "r+")
  uri = file.readline()
  while (uri != ""):
    otps.append(pyotp.parse_uri(uri))
    mi_otp = Gtk.MenuItem(otps[-1].issuer + ": " + otps[-1].name if otps[-1].issuer is not None else otps[-1].name)
    mi_otp.connect("activate", partial(lambda otp, _: cboard.set_text(otp.now(), -1), otps[-1]))
    menu.append(mi_otp)
    uri = file.readline()
except FileNotFoundError:
  file = open(os.path.expanduser("~/.local/share/trayotp.dat"), "w+")
file.close()

menu.append(Gtk.SeparatorMenuItem())
mi_quit = Gtk.MenuItem("Quit")
mi_quit.connect("activate", quit)
menu.append(mi_quit)
menu.show_all()

item = tray.Indicator.new("trayotp", "gcr-password", tray.IndicatorCategory.APPLICATION_STATUS)
item.set_status(tray.IndicatorStatus.ACTIVE)
item.set_menu(menu)
Gtk.main()
