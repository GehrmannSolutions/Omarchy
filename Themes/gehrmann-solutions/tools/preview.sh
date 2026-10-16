#!/usr/bin/env bash
# Take preview.png of the active theme without touching the visible screen: a headless 1920x1080
# output gets a workspace with two terminals (the theme's colors.toml in Neovim, tools/palette.sh),
# grim captures that output, and everything is removed again.
#
# usage: tools/preview.sh THEME_NAME OUT.png   (the theme must be installed and active)
# Needs: Hyprland (Lua config), foot, nvim, grim, jq, magick.
set -euo pipefail
NAME=${1:?theme name}; OUT=${2:?output png}
HERE=$(cd "$(dirname "$0")" && pwd)
THEME=$HOME/.config/omarchy/themes/$NAME
OUTPUT=GSPREVIEW
[[ -d $THEME ]] || { echo "preview.sh: $THEME is not installed" >&2; exit 1; }
[[ $(cat ~/.local/state/omarchy/current/theme.name) == "$NAME" ]] || { echo "preview.sh: $NAME is not the active theme" >&2; exit 1; }

cleanup() {
  for pid in $(hyprctl clients -j | jq -r '.[] | select(.class == "gs-preview") | .pid'); do kill "$pid" 2>/dev/null || true; done
  sleep 1
  hyprctl output remove "$OUTPUT" >/dev/null 2>&1 || true
}
trap cleanup EXIT

focused=$(hyprctl activeworkspace -j | jq -r .id)
hyprctl output create headless "$OUTPUT" >/dev/null
hyprctl repl "hl.monitor({ output = \"$OUTPUT\", mode = \"1920x1080\", position = \"20000x0\", scale = 1 })" >/dev/null
sleep 1
# the headless output brings its own workspace; new monitors take the focus, so give it back
WS=$(hyprctl monitors -j | jq -r --arg o "$OUTPUT" '.[] | select(.name == $o) | .activeWorkspace.id')
hyprctl dispatch "hl.dsp.focus({ workspace = \"$focused\" })" >/dev/null
# the windows go there silently, by their app id
hyprctl repl "return hl.window_rule({ match = { class = '^gs-preview\$' }, workspace = '$WS silent' })" >/dev/null

setsid foot -a gs-preview -D "$THEME" nvim -R colors.toml >/dev/null 2>&1 &
sleep 2
setsid foot -a gs-preview -D "$THEME" "$HERE/palette.sh" "$THEME" >/dev/null 2>&1 &
sleep 12   # Neovim's first-start messages fade
raw=$(mktemp --suffix=.png)
grim -o "$OUTPUT" "$raw"
magick "$raw" -resize 1800x1012! -strip "$OUT"
rm -f "$raw"
echo "preview: $OUT"
