"""GTK4 GUI to configure and manage timeBuzzer gesture profiles.

Each profile maps the five gestures (rotate clockwise/counter-clockwise,
tap, tap-and-hold, click) to an arbitrary shell command. "Live-Test" runs
the currently edited (not necessarily saved) mapping against the real
device so you can try it out before saving.
"""

from __future__ import annotations

import subprocess
from datetime import datetime

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk

from .gestures import GestureBuzzer
from .presets import PRESETS
from .profiles import ProfileStore

GESTURES = [
    ("rotate_cw", "Drehen im Uhrzeigersinn"),
    ("rotate_ccw", "Drehen gegen den Uhrzeigersinn"),
    ("tap", "Tippen"),
    ("tap_hold", "Tippen & Halten"),
    ("click", "Klicken"),
]


def run_command(command: str) -> None:
    command = command.strip()
    if command:
        subprocess.Popen(command, shell=True)


class TimeBuzzerWindow(Gtk.ApplicationWindow):
    def __init__(self, app: Gtk.Application):
        super().__init__(application=app, title="timeBuzzer Profile")
        self.set_default_size(900, 480)

        self.store = ProfileStore()
        self.entries: dict[str, Gtk.Entry] = {}
        self.preset_dropdowns: dict[str, Gtk.DropDown] = {}
        self.current_profile: str | None = None
        self.gesture_buzzer: GestureBuzzer | None = None

        root = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=0,
            margin_top=8,
            margin_bottom=8,
            margin_start=8,
            margin_end=8,
            hexpand=True,
            vexpand=True,
        )
        self.set_child(root)

        # --- sidebar toggle ("»"/"«" flip on click) ---
        self.sidebar_toggle_btn = Gtk.Button(label="«", vexpand=True)
        self.sidebar_toggle_btn.set_size_request(28, -1)
        self.sidebar_toggle_btn.connect("clicked", self.on_toggle_sidebar)
        root.append(self.sidebar_toggle_btn)

        # --- left: profile list (collapsible flyout, no animation) ---
        self.sidebar = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=4, vexpand=True, margin_start=4
        )
        left = self.sidebar
        root.append(self.sidebar)

        right = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8,
            hexpand=True,
            vexpand=True,
            margin_start=8,
        )
        root.append(right)

        self.profile_list = Gtk.ListBox(hexpand=True, vexpand=True)
        self.profile_list.connect("row-selected", self.on_profile_selected)
        left_scroll = Gtk.ScrolledWindow(min_content_width=240, hexpand=True, vexpand=True)
        left_scroll.set_child(self.profile_list)
        left.append(left_scroll)

        list_buttons = Gtk.Grid(row_spacing=4, column_spacing=4, column_homogeneous=True)
        left.append(list_buttons)
        for i, (label, handler) in enumerate(
            (
                ("Neu", self.on_new),
                ("Umbenennen", self.on_rename),
                ("Duplizieren", self.on_duplicate),
                ("Löschen", self.on_delete),
            )
        ):
            btn = Gtk.Button(label=label, hexpand=True)
            btn.connect("clicked", handler)
            list_buttons.attach(btn, i % 2, i // 2, 1, 1)

        # --- right: editor ---
        preset_labels = [label for label, _command in PRESETS]

        grid = Gtk.Grid(row_spacing=6, column_spacing=8, hexpand=True)
        grid.set_column_homogeneous(False)
        grid_scroll = Gtk.ScrolledWindow(
            hexpand=True,
            vscrollbar_policy=Gtk.PolicyType.NEVER,
            hscrollbar_policy=Gtk.PolicyType.AUTOMATIC,
        )
        grid_scroll.set_child(grid)
        right.append(grid_scroll)
        for i, (key, label) in enumerate(GESTURES):
            grid.attach(Gtk.Label(label=label, xalign=0, hexpand=False), 0, i, 1, 1)

            entry = Gtk.Entry(hexpand=True)
            entry.set_placeholder_text("Shell-Befehl, z.B. wpctl set-volume @DEFAULT_SINK@ 5%+")
            self.entries[key] = entry
            grid.attach(entry, 1, i, 1, 1)

            test_btn = Gtk.Button(label="Testen", hexpand=False)
            test_btn.connect("clicked", lambda _b, k=key: run_command(self.entries[k].get_text()))
            grid.attach(test_btn, 2, i, 1, 1)

            preset_dropdown = Gtk.DropDown.new_from_strings(preset_labels)
            preset_dropdown.set_enable_search(True)
            preset_dropdown.set_selected(Gtk.INVALID_LIST_POSITION)
            preset_dropdown.set_hexpand(False)
            preset_dropdown.set_size_request(230, -1)
            preset_dropdown.connect("notify::selected", self.on_preset_selected, key)
            self.preset_dropdowns[key] = preset_dropdown
            grid.attach(preset_dropdown, 3, i, 1, 1)

        action_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        right.append(action_row)

        save_btn = Gtk.Button(label="Speichern")
        save_btn.connect("clicked", self.on_save)
        action_row.append(save_btn)

        self.active_btn = Gtk.Button(label="Als aktiv setzen")
        self.active_btn.connect("clicked", self.on_set_active)
        action_row.append(self.active_btn)

        self.live_btn = Gtk.ToggleButton(label="Live-Test starten")
        self.live_btn.connect("toggled", self.on_toggle_live)
        action_row.append(self.live_btn)

        self.status_label = Gtk.Label(label="", xalign=0, wrap=True)
        right.append(self.status_label)

        self.log_buffer = Gtk.TextBuffer()
        log_view = Gtk.TextView(buffer=self.log_buffer, editable=False, vexpand=True)
        log_scroll = Gtk.ScrolledWindow(vexpand=True)
        log_scroll.set_child(log_view)
        right.append(log_scroll)

        self.connect("close-request", self.on_close)
        self.reload_profile_list()

    # ---- profile list management ----
    def reload_profile_list(self, select: str | None = None) -> None:
        child = self.profile_list.get_first_child()
        while child:
            nxt = child.get_next_sibling()
            self.profile_list.remove(child)
            child = nxt

        active = self.store.active
        target = select or active
        row_to_select = None
        for name in self.store.list():
            label = f"{name}  (aktiv)" if name == active else name
            row = Gtk.ListBoxRow()
            row.set_child(Gtk.Label(label=label, xalign=0, margin_start=4, margin_end=4))
            row.profile_name = name
            self.profile_list.append(row)
            if name == target:
                row_to_select = row
        if row_to_select:
            self.profile_list.select_row(row_to_select)
        else:
            self.current_profile = None

    def on_profile_selected(self, _listbox: Gtk.ListBox, row: Gtk.ListBoxRow | None) -> None:
        if row is None:
            self.current_profile = None
            for entry in self.entries.values():
                entry.set_text("")
            for dropdown in self.preset_dropdowns.values():
                dropdown.set_selected(Gtk.INVALID_LIST_POSITION)
            return
        name = row.profile_name
        self.current_profile = name
        config = self.store.load(name)
        for key, entry in self.entries.items():
            entry.set_text(config.get(key, ""))
        for dropdown in self.preset_dropdowns.values():
            dropdown.set_selected(Gtk.INVALID_LIST_POSITION)
        self.set_status(f"Profil '{name}' geladen")

    def on_preset_selected(self, dropdown: Gtk.DropDown, _pspec, key: str) -> None:
        position = dropdown.get_selected()
        if position == Gtk.INVALID_LIST_POSITION:
            return
        _label, command = PRESETS[position]
        self.entries[key].set_text(command)

    def on_toggle_sidebar(self, _btn: Gtk.Button) -> None:
        expand = not self.sidebar.get_visible()
        self.sidebar.set_visible(expand)
        self.sidebar_toggle_btn.set_label("«" if expand else "»")

    def on_new(self, _btn: Gtk.Button) -> None:
        self.prompt_name("Neues Profil", "", self.create_profile)

    def on_rename(self, _btn: Gtk.Button) -> None:
        if not self.current_profile:
            self.set_status("Kein Profil ausgewählt")
            return
        self.prompt_name("Profil umbenennen", self.current_profile, self.rename_profile)

    def rename_profile(self, new_name: str) -> None:
        old_name = self.current_profile
        if not old_name or not new_name or new_name == old_name:
            return
        if new_name in self.store.list():
            self.set_status(f"Name bereits vergeben: {new_name!r}")
            return
        self.store.rename(old_name, new_name)
        self.reload_profile_list(select=new_name)
        self.set_status(f"Profil '{old_name}' umbenannt zu '{new_name}'")

    def create_profile(self, name: str) -> None:
        if not name or name in self.store.list():
            self.set_status(f"Ungültiger oder bereits vorhandener Name: {name!r}")
            return
        self.store.save(name, {})
        self.reload_profile_list(select=name)

    def on_duplicate(self, _btn: Gtk.Button) -> None:
        if not self.current_profile:
            self.set_status("Kein Profil ausgewählt")
            return
        self.prompt_name(
            "Profil duplizieren", f"{self.current_profile}-kopie", self.duplicate_profile
        )

    def duplicate_profile(self, new_name: str) -> None:
        if not new_name or new_name in self.store.list():
            self.set_status(f"Ungültiger oder bereits vorhandener Name: {new_name!r}")
            return
        config = {key: entry.get_text() for key, entry in self.entries.items()}
        self.store.save(new_name, config)
        self.reload_profile_list(select=new_name)

    def on_delete(self, _btn: Gtk.Button) -> None:
        if not self.current_profile:
            self.set_status("Kein Profil ausgewählt")
            return
        name = self.current_profile
        dialog = Gtk.AlertDialog(message=f"Profil „{name}“ wirklich löschen?")
        dialog.set_buttons(["Abbrechen", "Löschen"])
        dialog.set_cancel_button(0)
        dialog.set_default_button(0)

        def on_response(d: Gtk.AlertDialog, result: object) -> None:
            try:
                choice = d.choose_finish(result)
            except GLib.Error:
                return
            if choice == 1:
                self.store.delete(name)
                if self.store.active == name:
                    self.store.active = None
                self.reload_profile_list()
                self.set_status(f"Profil '{name}' gelöscht")

        dialog.choose(self, None, on_response)

    def prompt_name(self, title: str, default: str, callback) -> None:
        dialog = Gtk.Dialog(title=title, transient_for=self, modal=True)
        dialog.add_buttons("Abbrechen", Gtk.ResponseType.CANCEL, "OK", Gtk.ResponseType.OK)
        entry = Gtk.Entry(
            text=default, margin_top=8, margin_bottom=8, margin_start=8, margin_end=8
        )
        entry.set_activates_default(True)
        dialog.set_default_response(Gtk.ResponseType.OK)
        dialog.get_content_area().append(entry)

        def on_response(d: Gtk.Dialog, response: int) -> None:
            if response == Gtk.ResponseType.OK:
                callback(entry.get_text().strip())
            d.destroy()

        dialog.connect("response", on_response)
        dialog.present()

    # ---- save / activate ----
    def on_save(self, _btn: Gtk.Button) -> None:
        if not self.current_profile:
            self.set_status("Kein Profil ausgewählt")
            return
        config = {key: entry.get_text() for key, entry in self.entries.items()}
        self.store.save(self.current_profile, config)
        self.set_status(f"Profil '{self.current_profile}' gespeichert")

    def on_set_active(self, _btn: Gtk.Button) -> None:
        if not self.current_profile:
            self.set_status("Kein Profil ausgewählt")
            return
        self.store.active = self.current_profile
        self.reload_profile_list(select=self.current_profile)
        self.set_status(f"Profil '{self.current_profile}' ist jetzt aktiv")

    # ---- live test ----
    def on_toggle_live(self, btn: Gtk.ToggleButton) -> None:
        if btn.get_active():
            config = {key: entry.get_text() for key, entry in self.entries.items()}
            try:
                self.gesture_buzzer = GestureBuzzer(
                    on_rotate_cw=lambda n: self.fire("rotate_cw", config, n),
                    on_rotate_ccw=lambda n: self.fire("rotate_ccw", config, n),
                    on_tap=lambda: self.fire("tap", config),
                    on_tap_hold=lambda: self.fire("tap_hold", config),
                    on_click=lambda: self.fire("click", config),
                )
            except FileNotFoundError as e:
                self.set_status(str(e))
                btn.set_active(False)
                return
            self.gesture_buzzer.start()
            btn.set_label("Live-Test stoppen")
            self.set_status(f"Live-Test läuft auf {self.gesture_buzzer.device}")
        else:
            if self.gesture_buzzer:
                self.gesture_buzzer.stop()
                self.gesture_buzzer = None
            btn.set_label("Live-Test starten")
            self.set_status("Live-Test gestoppt")

    def fire(self, key: str, config: dict, count: int = 1) -> None:
        # Called from the device's background reader thread - hand off to
        # the GTK main loop before touching any widgets or subprocess.
        GLib.idle_add(self._fire_main_thread, key, config, count)

    def _fire_main_thread(self, key: str, config: dict, count: int) -> bool:
        command = config.get(key, "")
        timestamp = datetime.now().strftime("%H:%M:%S")
        suffix = f" x{count}" if count > 1 else ""
        if command.strip():
            run_command(command)
            self.log(f"[{timestamp}] {key}{suffix} -> {command}")
        else:
            self.log(f"[{timestamp}] {key}{suffix} (kein Befehl konfiguriert)")
        return False

    def log(self, line: str) -> None:
        end = self.log_buffer.get_end_iter()
        self.log_buffer.insert(end, line + "\n")

    def set_status(self, text: str) -> None:
        self.status_label.set_text(text)

    def on_close(self, _win: Gtk.ApplicationWindow) -> bool:
        if self.gesture_buzzer:
            self.gesture_buzzer.stop()
        return False


class TimeBuzzerApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="solutions.gehrmann.timebuzzer")

    def do_activate(self) -> None:
        win = self.get_active_window()
        if not win:
            win = TimeBuzzerWindow(self)
        win.present()


def main() -> None:
    TimeBuzzerApp().run()


if __name__ == "__main__":
    main()
