import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository.GObject import Signal
import pyotp
import hashlib

class SavedAccountsWindow(Gtk.Window):
  def __init__(self, saved_otps):
    super().__init__(title="Edit Saved Accounts", icon_name="gcr-password")
    self.saved_otps = saved_otps
    self.set_default_size(400,300)
    self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    
    self.otp_list = Gtk.ListBox()
    for otp in saved_otps:
      self.otp_list.add(Gtk.Label(otp.issuer + ": " + otp.name if otp.issuer is not None else otp.name))
    self.main_box.pack_start(self.otp_list, True, True, 0)

    self.footer_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
    self.new_button = Gtk.Button.new_from_stock(Gtk.STOCK_NEW)
    self.new_button.connect("clicked", self.new_acct)
    self.edit_button = Gtk.Button.new_from_stock(Gtk.STOCK_EDIT)
    self.edit_button.connect("clicked", self.edit_acct)
    self.delete_button = Gtk.Button.new_from_stock(Gtk.STOCK_DELETE)
    self.delete_button.connect("clicked", self.delete_acct)
    self.footer_box.pack_start(self.new_button, True, False, 0)
    self.footer_box.pack_start(self.edit_button, True, False, 0)
    self.footer_box.pack_start(self.delete_button, True, False, 0)
    self.main_box.pack_start(self.footer_box, False, False, 5)

    self.add(self.main_box)
    self.show_all()
  
  @Signal
  def updated(self):
    pass

  def new_acct(self, _):
    def add_acct(_):
      if (edit_win.changed):
        self.saved_otps.append(edit_win.otp)
        self.otp_list.add(Gtk.Label(edit_win.otp.issuer + ": " + edit_win.otp.name if edit_win.otp.issuer is not None else edit_win.otp.name))
        self.otp_list.show_all()
        self.updated.emit()
    edit_win = AcctEditingWindow()
    edit_win.set_transient_for(self)
    edit_win.connect("destroy", add_acct)
    
  def edit_acct(self, _):
    def update_acct(_):
      if (edit_win.changed):
        sel.get_child().set_label(edit_win.otp.issuer + ": " + edit_win.otp.name if edit_win.otp.issuer is not None else edit_win.otp.name)
        self.updated.emit()
    sel = self.otp_list.get_selected_row()
    if (sel is not None):
      edit_win = AcctEditingWindow(self.saved_otps[sel.get_index()])
      edit_win.set_transient_for(self)
      edit_win.connect("destroy", update_acct)

  def delete_acct(self, _):
    sel = self.otp_list.get_selected_row()
    if (sel is not None):
      del self.saved_otps[sel.get_index()]
      self.otp_list.remove(sel)
      self.updated.emit()

class AcctEditingWindow(Gtk.Window):
  def __init__(self, otp=None):
    super().__init__(title="Editing Account", icon_name="document-edit")
    self.otp = otp
    self.changed = False
    self.set_default_size(600,300)
    self.main_grid = Gtk.Grid(column_homogeneous=True)
    self.main_grid.attach(Gtk.Label("Account name:"), 0, 0, 1, 1)
    self.txt_name = Gtk.Entry()
    self.main_grid.attach(self.txt_name, 1, 0, 1, 1)
    self.main_grid.attach(Gtk.Label("Issuer:"), 0, 1, 1, 1)
    self.txt_issuer = Gtk.Entry()
    self.main_grid.attach(self.txt_issuer, 1, 1, 1, 1)
    self.main_grid.attach(Gtk.Label("Secret:"), 0, 2, 1, 1)
    self.txt_secret = Gtk.Entry()
    self.main_grid.attach(self.txt_secret, 1, 2, 1, 1)
    self.main_grid.attach(Gtk.Label("Algorithm:"), 0, 3, 1, 1)
    self.combo_algo = Gtk.ComboBoxText()
    self.combo_algo.append_text("SHA-1")
    self.combo_algo.append_text("SHA-256")
    self.combo_algo.append_text("SHA-512")
    self.combo_algo.set_active(0)
    self.main_grid.attach(self.combo_algo, 1, 3, 1, 1)
    self.main_grid.attach(Gtk.Label("Interval (seconds):"), 0, 4, 1, 1)
    self.spn_interval = Gtk.SpinButton.new_with_range(1, 90, 1)
    self.main_grid.attach(self.spn_interval, 1, 4, 1, 1)
    self.main_grid.attach(Gtk.Label("Digits:"), 0, 5, 1, 1)
    self.spn_digits = Gtk.SpinButton.new_with_range(1, 10, 1)
    self.main_grid.attach(self.spn_digits, 1, 5, 1, 1)

    self.cancel_button = Gtk.Button.new_from_stock(Gtk.STOCK_CANCEL)
    self.cancel_button.set_vexpand_set(True)
    self.cancel_button.set_vexpand(True)
    self.cancel_button.set_valign(Gtk.Align.END)
    self.cancel_button.connect("clicked", lambda _: self.destroy())
    self.main_grid.attach(self.cancel_button, 0, 6, 1, 1)
    self.save_button = Gtk.Button.new_from_stock(Gtk.STOCK_SAVE)
    self.save_button.set_vexpand_set(True)
    self.save_button.set_vexpand(True)
    self.save_button.set_valign(Gtk.Align.END)
    self.save_button.connect("clicked", self.save_acct)
    self.main_grid.attach(self.save_button, 1, 6, 1, 1)

    self.add(self.main_grid)
    if (otp is not None):
      self.txt_name.set_text(otp.name)
      if (otp.issuer is not None): self.txt_issuer.set_text(otp.issuer)
      self.txt_secret.set_text(otp.secret)
      if (otp.digest.__name__ == "openssl_sha256"):
        self.combo_algo.set_active(1)
      elif (otp.digest.__name__ == "openssl_sha256"):
        self.combo_algo.set_active(2)
      else:
        self.combo_algo.set_active(0)
      self.spn_interval.set_value(otp.interval)
      self.spn_digits.set_value(otp.digits)
    self.show_all()

  def save_acct(self, _):
    if (self.txt_secret.get_text() == ""):
      dialog = Gtk.MessageDialog(title="No secret specified", text="Please enter a valid secret.", buttons=Gtk.ButtonsType.OK, message_type=Gtk.MessageType.ERROR)
      dialog.run()
      dialog.destroy()
      return
    self.changed = True
    if (self.otp is None):
      self.otp = pyotp.TOTP("")
    self.otp.name = self.txt_name.get_text()
    self.otp.issuer = self.txt_issuer.get_text() if self.txt_issuer.get_text() != "" else None
    self.otp.secret = self.txt_secret.get_text()
    if (self.combo_algo.get_active_text() == "SHA-256"):
      self.otp.digest = hashlib.sha256
    elif (self.combo_algo.get_active_text() == "SHA-512"):
      self.otp.digest = hashlib.sha512
    else:
      self.otp.digest = hashlib.sha1
    self.otp.interval = int(self.spn_interval.get_value())
    self.otp.digits = int(self.spn_digits.get_value())
    self.destroy()
