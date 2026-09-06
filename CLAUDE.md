# timebuzzer-control

## Zweck
Python-Toolkit, um das physische timeBuzzer-USB-Rad (Zeiterfassungs-Gerät von
Ideas in Logic GbR) als generisches Eingabegerät zu nutzen — losgelöst von der
timeBuzzer-Cloud-Software. Stellt Rotation, Touch und Klick als Callbacks
bereit, plus benannte/speicherbare Profile, damit Steuerskripte je nach
aktivem Profil unterschiedlich reagieren können.

## Reverse-Engineering-Ergebnis
- Gerät: USB VID `16d0` / PID `1170`, meldet sich als **USB-MIDI-Class-
  Compliant-Gerät** (Audio-Control-Interface + MIDI-Streaming-Interface,
  läuft über `snd-usb-audio`). Kein HID, kein proprietäres Protokoll —
  erscheint unter Linux als normales ALSA-Rawmidi-Gerät
  (`/proc/asound/cards` → "timeBuzzer", Device `/dev/snd/midiC<N>D0`).
- Ermittelt durch Live-Mitschnitt mit `amidi -p hw:<N>,0,0 -d -T raw`
  während gezielter Interaktion (nichts anfassen / berühren / drehen CW+CCW /
  klicken), um Ruhesignal von echten Events zu unterscheiden.
- Protokoll: alle Events sind Control-Change-Nachrichten auf MIDI-Kanal 12
  (Statusbyte `0xBB`):
  - **CC 80** — Encoder-Zähler, 7-Bit mit Wraparound (0–127). Zählt bei
    Drehung im Uhrzeigersinn hoch, gegen den Uhrzeigersinn runter, ein
    Schritt pro Rasterung. Richtung/Menge = Differenz zum letzten Wert
    (mod 128, vorzeichenbehaftet).
  - **CC 81** — Touch-Heartbeat, alle ~1,5s gesendet unabhängig vom Zustand:
    `127` = kein Kontakt, `0` = Finger liegt auf.
  - **CC 82** — Klick-Event, nur beim mechanischen Runterdrücken: `127`
    (Druck) gefolgt kurz danach von `0` (Loslassen).
- Die offizielle timeBuzzer-Cloud-API (github.com/timeBuzzer/timebuzzer-open-
  api-doc) betrifft nur Projekte/Zeiteinträge in der Cloud, nicht das lokale
  USB-Protokoll — für dieses Projekt nicht relevant.

## Entscheidungen
- 2026-09-06: Direktes Lesen der ALSA-Rawmidi-Bytes (`/dev/snd/midiC<N>D0`)
  statt einer MIDI-Library (`mido`/`python-rtmidi`), weil auf dem System kein
  `pip`/AUR-Helper verfügbar war und die Nachrichten trivial (3-Byte-CC) sind
  — keine externe Abhängigkeit nötig.
- 2026-09-06: Nutzer dauerhaft zur `audio`-Gruppe hinzugefügt
  (`sudo usermod -aG audio $USER`), damit `/dev/snd/midiC*` ohne sudo lesbar
  ist. Wirkt erst nach Neu-Login/`newgrp`.
- 2026-09-06: Profile sind bewusst generisch (beliebiges JSON-Dict pro Name,
  gespeichert unter `~/.config/timebuzzer/profiles/<name>.json`, aktives
  Profil in `~/.config/timebuzzer/active_profile`) — das Toolkit legt keine
  Bedeutung der Profil-Inhalte fest, das entscheidet das jeweilige
  Steuerskript.

## Nutzung
```python
from timebuzzer import TimeBuzzer

tb = TimeBuzzer(
    on_rotate=lambda delta: print(f"rotate {delta:+d}"),
    on_touch=lambda active: print("touch" if active else "release"),
    on_click=lambda: print("click"),
)
tb.run()  # blockierend; alternativ tb.start()/tb.stop() für Hintergrund-Thread
```

Profile: siehe `examples/profiles_demo.py` (`save <name>`, `list`, oder ohne
Argument mit dem aktiven Profil starten).

## GUI (`timebuzzer/gui.py`, Start via `examples/gui.py`)
GTK4/PyGObject-Editor (bereits im System vorhanden, keine Installation
nötig) zum Konfigurieren, Speichern/Umbenennen/Duplizieren/Löschen von
Profilen. Pro Profil 5 Gesten (Drehen im/gegen Uhrzeigersinn, Tippen,
Tippen & Halten, Klicken) je einem Shell-Befehl zugeordnet, mit
durchsuchbarem Presets-Dropdown (`timebuzzer/presets.py`) und Live-Test
gegen das echte Gerät. "Tippen"/"Tippen & Halten" gibt es nicht im rohen
Protokoll — `timebuzzer/gestures.py` (`GestureBuzzer`) leitet sie per
Timing-Schwellwert (Standard 0,5s) aus dem Touch-Signal ab, zusätzlich zu
`rotate_cw`/`rotate_ccw` (Vorzeichen der Rotation) und `click` (Weiterleitung).

### GTK4-Stolperstein: Sidebar ein-/ausklappen
Ein `Gtk.Revealer` kollabiert **nicht zuverlässig auf 0px**, sobald der
eingeklappte Inhalt Widgets mit einer theme-/property-seitig erzwungenen
Mindestbreite enthält (z.B. `ScrolledWindow.min_content_width`, oder
`Gtk.Button` durch Adwaita-CSS `min-width`) — der Revealer blieb bei
`child_revealed=False` dauerhaft bei einem Bruchteil der ursprünglichen
Breite hängen, unabhängig von `transition_duration` (auch bei 0 oder 16ms).
Reines Ein-/Ausblenden der Sidebar-Box per `widget.set_visible(bool)`
funktioniert zuverlässig (schließt das Widget komplett von der
Größenberechnung aus) und wurde daher statt `Gtk.Revealer` verwendet —
passt auch besser, da ohnehin keine Animation gewünscht war.

## Offene nächste Schritte
- Konkrete Standard-Profile (z.B. fertig konfiguriert für Mediensteuerung)
  sind nicht vorausgefüllt — Nutzer legt sie über die GUI selbst an.
