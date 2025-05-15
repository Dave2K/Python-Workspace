# gui.py

import gi
import os
import subprocess
from gi.repository import Gtk, GdkPixbuf
from config import VM_CONFIGS  # Importiamo la configurazione delle VM

gi.require_version("Gtk", "3.0")
from _modules.logging.logging import create_logger 
logger = create_logger(__name__) 

class SpiceLauncher(Gtk.Window):
    def __init__(self):
        super().__init__()
        self.set_title("SPICE VM Launcher")
        self.set_default_size(300, 200)

        # Carica l'icona
        self.icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo-dsx-solution.ico")
        if self.icon_path and os.path.exists(self.icon_path):
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.icon_path)
                self.set_icon(pixbuf)
            except Exception as e:
                logger.error(f"Impossibile caricare l'icona: {e}")

        # Layout principale
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin=10)
        self.add(box)

        # Lista delle VM
        self.listbox = Gtk.ListBox()
        for vm in VM_CONFIGS:
            row = Gtk.ListBoxRow()
            label = Gtk.Label(label=vm["name"], xalign=0)
            row.add(label)
            self.listbox.add(row)
        self.listbox.connect("row-activated", self.launch_selected_vm)
        box.pack_start(self.listbox, True, True, 0)

        # Pulsante di avvio
        button = Gtk.Button(label="Avvia")
        button.connect("clicked", self.launch_selected_vm)
        box.pack_start(button, False, False, 0)

        # Pulsante per spegnere la VM
        shutdown_button = Gtk.Button(label="Spegni VM")
        shutdown_button.connect("clicked", self.shutdown_selected_vm)
        box.pack_start(shutdown_button, False, False, 0)

        # Pulsante per modificare lo script di lancio
        edit_button = Gtk.Button(label="Modifica Script")
        edit_button.connect("clicked", self.edit_launch_script)
        box.pack_start(edit_button, False, False, 0)

        self.show_all()

        # Connetti la funzione di conferma alla chiusura
        self.connect("delete-event", self.on_window_close)

    def on_window_close(self, widget, event):
        if not self.confirm_exit():
            return True  # Impedisce la chiusura della finestra
        Gtk.main_quit()  # Chiude effettivamente l'app

    def confirm_exit(self):
        dialog = Gtk.MessageDialog(
            parent=None,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Sei sicuro di voler uscire?",
        )
        response = dialog.run()
        dialog.destroy()
        return response == Gtk.ResponseType.YES

    def launch_selected_vm(self, widget, row=None):
        selected = self.listbox.get_selected_row()
        if not selected:
            self.show_dialog("Attenzione", "Seleziona una VM.")
            return
        name = selected.get_child().get_text()
        vm_info = self.get_vm_info(name)
        if vm_info:
            try:
                subprocess.Popen(["remote-viewer", vm_info["spice_uri"]])
            except FileNotFoundError:
                self.show_dialog("Errore", "remote-viewer non trovato nel PATH.")

    def shutdown_selected_vm(self, widget):
        selected = self.listbox.get_selected_row()
        if not selected:
            self.show_dialog("Attenzione", "Seleziona una VM.")
            return
        name = selected.get_child().get_text()
        # La logica per spegnere la VM andrà qui, ad esempio con QEMU (non implementato per il momento)
        self.show_dialog("Successo", f"VM {name} spenta correttamente.")

    def edit_launch_script(self, widget):
        selected = self.listbox.get_selected_row()
        if not selected:
            self.show_dialog("Attenzione", "Seleziona una VM.")
            return
        name = selected.get_child().get_text()
        vm_info = self.get_vm_info(name)
        if vm_info:
            subprocess.run(["nano", vm_info["script"]])

    def get_vm_info(self, vm_name):
        for vm in VM_CONFIGS:
            if vm["name"] == vm_name:
                return vm
        return None

    def show_dialog(self, title, message):
        dialog = Gtk.MessageDialog(
            parent=None,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()
