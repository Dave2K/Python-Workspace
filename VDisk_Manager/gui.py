"""Interfaccia GTK per gestire immagini disco (.img, .qcow2) con mount/umount."""
import gi
import os
import subprocess
from gi.repository import Gtk
from config import load_config, save_config

gi.require_version("Gtk", "3.0")

IMG_EXTENSIONS = (".img", ".qcow2")

class DiskImageManager(Gtk.Window):
    """
    Finestra principale:
    - mostra lista file .img/.qcow2
    - pulsanti: Aggiorna, Seleziona cartella, Apri, Elimina,
      Informazioni, Crea Immagine, Monta, Smonta
    - persistenza dell’ultimo percorso scelto
    - tiene traccia dei mount attivi in self.mounted
    """
    def __init__(self):
        Gtk.Window.__init__(self, title="Disk Image Manager")
        self.set_border_width(10)
        self.set_default_size(600, 500)

        cfg = load_config()
        self.img_dir = cfg.get("last_dir", "/home/davide/Documents/src/Python-Workspace/")
        self.mounted = {}  # dict: path_img -> mount_point

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        # Riga dei pulsanti principali
        button_box = Gtk.Box(spacing=6)
        self.refresh_button = Gtk.Button(label="Aggiorna")
        self.refresh_button.connect("clicked", self.on_refresh_clicked)
        self.select_button = Gtk.Button(label="Seleziona cartella")
        self.select_button.connect("clicked", self.on_select_folder_clicked)
        button_box.pack_start(self.refresh_button, False, False, 0)
        button_box.pack_start(self.select_button, False, False, 0)
        vbox.pack_start(button_box, False, False, 0)

        # TreeView per lista immagini
        self.liststore = Gtk.ListStore(str, str)
        self.treeview = Gtk.TreeView(model=self.liststore)
        renderer = Gtk.CellRendererText()
        self.treeview.append_column(Gtk.TreeViewColumn("File", renderer, text=0))
        self.treeview.append_column(Gtk.TreeViewColumn("Dimensione", renderer, text=1))
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.add(self.treeview)
        vbox.pack_start(scroll, True, True, 0)

        # Pulsanti di azione sul file selezionato
        action_box = Gtk.Box(spacing=6)
        self.open_button   = Gtk.Button(label="Apri")
        self.delete_button = Gtk.Button(label="Elimina")
        self.info_button   = Gtk.Button(label="Informazioni")
        self.create_button = Gtk.Button(label="Crea Immagine")
        self.mount_button  = Gtk.Button(label="Monta")
        self.umount_button = Gtk.Button(label="Smonta")

        self.open_button.connect("clicked",   self.on_open_clicked)
        self.delete_button.connect("clicked", self.on_delete_clicked)
        self.info_button.connect("clicked",   self.on_info_clicked)
        self.create_button.connect("clicked", self.on_create_clicked)
        self.mount_button.connect("clicked",  self.on_mount_clicked)
        self.umount_button.connect("clicked", self.on_umount_clicked)

        for btn in (self.open_button, self.delete_button,
                    self.info_button, self.create_button,
                    self.mount_button, self.umount_button):
            action_box.pack_start(btn, False, False, 0)
        vbox.pack_start(action_box, False, False, 0)

        self.refresh_list()

    def refresh_list(self, *_):
        """Ricarica in lista tutti i file con estensione target."""
        self.liststore.clear()
        try:
            for fn in os.listdir(self.img_dir):
                if fn.endswith(IMG_EXTENSIONS):
                    full = os.path.join(self.img_dir, fn)
                    size_mb = os.path.getsize(full) / (1024**2)
                    self.liststore.append([fn, f"{size_mb:.2f} MB"])
        except Exception as e:
            self._show_error("Cartella non valida", str(e))

    def get_selected_path(self):
        """Restituisce il path completo del file selezionato o None."""
        sel = self.treeview.get_selection()
        model, itr = sel.get_selected()
        if itr:
            return os.path.join(self.img_dir, model[itr][0])
        return None

    def on_refresh_clicked(self, _):
        self.refresh_list()

    def on_select_folder_clicked(self, _):
        dlg = Gtk.FileChooserDialog(
            title="Scegli cartella", parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                     Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        )
        if dlg.run() == Gtk.ResponseType.OK:
            self.img_dir = dlg.get_filename()
            save_config({"last_dir": self.img_dir})
            self.refresh_list()
        dlg.destroy()

    def on_open_clicked(self, _):
        path = self.get_selected_path()
        if path:
            subprocess.Popen(["xdg-open", path])

    def on_delete_clicked(self, _):
        path = self.get_selected_path()
        if path:
            dlg = Gtk.MessageDialog(parent=self, flags=0,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO, text="Eliminare?")
            dlg.format_secondary_text(path)
            if dlg.run() == Gtk.ResponseType.YES:
                os.remove(path)
                self.refresh_list()
            dlg.destroy()

    def on_info_clicked(self, _):
        path = self.get_selected_path()
        if path and os.path.exists(path):
            sz = os.path.getsize(path)/(1024**2)
            dlg = Gtk.MessageDialog(parent=self, flags=0,
                message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK,
                text="Informazioni file")
            dlg.format_secondary_text(f"Percorso: {path}\nDimensione: {sz:.2f} MB")
            dlg.run(); dlg.destroy()

    def on_create_clicked(self, _):
        dlg = Gtk.Dialog(title="Crea nuova immagine", parent=self, flags=0)
        dlg.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                        Gtk.STOCK_OK, Gtk.ResponseType.OK)
        area = dlg.get_content_area()
        grid = Gtk.Grid(margin=10, column_spacing=10, row_spacing=10)
        entry = Gtk.Entry(); entry.set_placeholder_text("Nome senza estensione")
        combo = Gtk.ComboBoxText(); combo.append_text(".img"); combo.append_text(".qcow2")
        size_entry = Gtk.Entry(); size_entry.set_placeholder_text("Dimensione MB")
        grid.attach(Gtk.Label("Nome:"), 0, 0, 1, 1)
        grid.attach(entry,      1, 0, 1, 1)
        grid.attach(Gtk.Label("Estensione:"), 0, 1, 1, 1)
        grid.attach(combo,      1, 1, 1, 1)
        grid.attach(Gtk.Label("Dimensione:"), 0, 2, 1, 1)
        grid.attach(size_entry, 1, 2, 1, 1)
        area.add(grid); dlg.show_all()

        if dlg.run() == Gtk.ResponseType.OK:
            name = entry.get_text().strip()
            ext  = combo.get_active_text()
            try:
                mb = int(size_entry.get_text())
                path = os.path.join(self.img_dir, name + ext)
                if ext == ".img":
                    with open(path, "wb") as f: f.truncate(mb * 1024 * 1024)
                else:
                    subprocess.check_call(
                        ["qemu-img", "create", "-f", "qcow2", path, f"{mb}M"]
                    )
                self.refresh_list()
            except Exception as e:
                self._show_error("Errore creazione", str(e))
        dlg.destroy()

    def on_mount_clicked(self, _):
        """
        Monta l'immagine selezionata in r/w usando guestmount:
        - crea auto una dir di mount
        - salva in self.mounted
        """
        path = self.get_selected_path()
        if not path:
            return
        if path in self.mounted:
            self._show_error("Già montata", f"{path} è già montata.")
            return

        mount_dir = os.path.join(self.img_dir, os.path.basename(path) + "_mnt")
        os.makedirs(mount_dir, exist_ok=True)
        try:
            subprocess.check_call([
                "guestmount", "-a", path, "-i", "--rw", mount_dir
            ])
            self.mounted[path] = mount_dir
        except Exception as e:
            self._show_error("Errore mount", str(e))

    def on_umount_clicked(self, _):
        """
        Smonta l'immagine precedentemente montata chiamando fusermount -u
        e rimuove la dir di mount se vuota.
        """
        path = self.get_selected_path()
        if not path or path not in self.mounted:
            self._show_error("Non montata", "Seleziona prima un file montato.")
            return

        mount_dir = self.mounted[path]
        try:
            subprocess.check_call(["fusermount", "-u", mount_dir])
            # se vuota, rimuovo la cartella
            if not os.listdir(mount_dir):
                os.rmdir(mount_dir)
            del self.mounted[path]
        except Exception as e:
            self._show_error("Errore umount", str(e))

    def _show_error(self, title, msg):
        """Dialog d’errore generico."""
        dlg = Gtk.MessageDialog(parent=self, flags=0,
            message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK,
            text=title)
        dlg.format_secondary_text(msg)
        dlg.run(); dlg.destroy()

def run_app():
    """Avvia l’applicazione."""
    win = DiskImageManager()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
