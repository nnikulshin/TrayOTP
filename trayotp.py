#!/usr/bin/python
import os
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, AyatanaAppIndicator3 as tray
import pyotp
from dialogs import SavedAccountsWindow
from functools import partial

cboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
otps = []
otp_mis = []
menu = Gtk.Menu()
win = None

try:
  file = open(os.path.expanduser("~/.local/share/trayotp.dat"), "r+")
except FileNotFoundError:
  pass
else:
  uri = file.readline()
  while (uri != ""):
    otps.append(pyotp.parse_uri(uri))
    mi_otp = Gtk.MenuItem(otps[-1].issuer + ": " + otps[-1].name if otps[-1].issuer is not None else otps[-1].name)
    mi_otp.connect("activate", partial(lambda otp, _: cboard.set_text(otp.now(), -1), otps[-1]))
    menu.append(mi_otp)
    otp_mis.append(mi_otp)
    uri = file.readline()
  file.close()

def quit(_):
  Gtk.main_quit()

def update_menu_and_file(_):
  global otp_mis, win
  for mi_otp in otp_mis:
    mi_otp.destroy()
  otp_mis = []
  file = open(os.path.expanduser("~/.local/share/trayotp.dat"), "w")
  for otp in otps:
    mi_otp = Gtk.MenuItem(otp.issuer + ": " + otp.name if otp.issuer is not None else otp.name)
    mi_otp.connect("activate", partial(lambda o, _: cboard.set_text(o.now(), -1), otp))
    menu.insert(mi_otp, len(otp_mis))
    otp_mis.append(mi_otp)
    file.write(otp.provisioning_uri() + "\n")
  menu.show_all()
  file.close()
  win = None

def edit(_):
  global win
  if (win is None):
    win = SavedAccountsWindow(otps)
    win.connect("destroy", update_menu_and_file)

menu.append(Gtk.SeparatorMenuItem())
mi_edit = Gtk.MenuItem("Edit Saved Accounts")
mi_edit.connect("activate", edit)
menu.append(mi_edit)
mi_quit = Gtk.MenuItem("Quit")
mi_quit.connect("activate", quit)
menu.append(mi_quit)
menu.show_all()

item = tray.Indicator.new("trayotp", "gcr-password", tray.IndicatorCategory.SYSTEM_SERVICES)
item.set_status(tray.IndicatorStatus.ACTIVE)
item.set_menu(menu)
Gtk.main()
