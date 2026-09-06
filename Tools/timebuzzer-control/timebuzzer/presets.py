"""Curated shell-command suggestions offered in the GUI's presets dropdown.

Purely suggestions for a Hyprland/PipeWire Linux desktop (Omarchy) - picking
one just fills the command entry, which stays freely editable. None of the
underlying tools are guaranteed to be installed.
"""

PRESETS: list[tuple[str, str]] = [
    ("Audio: Lautstärke +5%", "wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%+"),
    ("Audio: Lautstärke -5%", "wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-"),
    ("Audio: Stumm umschalten", "wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"),
    ("Audio: Mikrofon stumm umschalten", "wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle"),
    ("Medien: Play/Pause", "playerctl play-pause"),
    ("Medien: Nächster Titel", "playerctl next"),
    ("Medien: Vorheriger Titel", "playerctl previous"),
    ("Medien: Stop", "playerctl stop"),
    ("Helligkeit: +10%", "brightnessctl set +10%"),
    ("Helligkeit: -10%", "brightnessctl set 10%-"),
    ("Hyprland: Workspace weiter", "hyprctl dispatch workspace +1"),
    ("Hyprland: Workspace zurück", "hyprctl dispatch workspace -1"),
    ("Hyprland: Fenster schließen", "hyprctl dispatch killactive"),
    ("Hyprland: Nächstes Fenster fokussieren", "hyprctl dispatch cyclenext"),
    ("Hyprland: Vollbild umschalten", "hyprctl dispatch fullscreen"),
    ("Hyprland: Floating umschalten", "hyprctl dispatch togglefloating"),
    ("Hyprland: Fenster verschieben (nächster Monitor)", "hyprctl dispatch movewindow mon:+1"),
    ("System: Bildschirm sperren", "hyprlock"),
    (
        "System: Screenshot (Bereich auswählen)",
        'grim -g "$(slurp)" ~/Pictures/screenshot-$(date +%s).png',
    ),
    ("System: Screenshot (ganzer Bildschirm)", "grim ~/Pictures/screenshot-$(date +%s).png"),
    ("System: Benachrichtigung anzeigen", "notify-send 'timeBuzzer' 'Geste ausgelöst'"),
]
