#!/bin/bash
# The Gehrmann Solutions boot screen: the GS logo with a breathing glow, as the Plymouth theme
# "gehrmann-solutions" (this folder's files, built for this theme's colours).
#
#   install.sh [--no-initramfs]   install and select it, then rebuild the initramfs (mkinitcpio -P)
#   install.sh remove             back to Omarchy's own boot screen (omarchy theme), rebuild
#   install.sh status
#
# It sets DeviceScale=1 in /etc/plymouth/plymouthd.conf: the theme sizes itself from the screen
# height with sharp, high-resolution images, while a device scale of 2 (high-DPI screens) would
# draw them at double size and soft. `remove` takes that line out again.
# `omarchy plymouth set …` selects Omarchy's boot screen again; a post-update hook reports when
# that happened, so it can be installed again.
# Kernels whose initramfs is not built from a mkinitcpio preset need their own rebuild
# (--no-initramfs skips mkinitcpio -P).
set -euo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
NAME=gehrmann-solutions
DEST=/usr/share/plymouth/themes/$NAME
CONF=/etc/plymouth/plymouthd.conf
MARK="# gehrmann-solutions plymouth: DeviceScale"
HOOK="$HOME/.config/omarchy/hooks/post-update.d/gs-plymouth.hook"
FILES=("$NAME.plymouth" "$NAME.script" logo-glow.png logo-shapes.png entry.png lock.png bullet.png progress_box.png progress_bar.png)

say() { echo "gs-plymouth: $*"; }
fail() { echo "gs-plymouth: $*" >&2; exit 1; }

current() { plymouth-set-default-theme 2>/dev/null || true; }

rebuild() {
  [[ ${1:-} == --no-initramfs ]] && { say "initramfs not rebuilt (--no-initramfs)"; return; }
  sudo mkinitcpio -P
}

case ${1:-install} in
install | --no-initramfs)
  [[ ${1:-} == --no-initramfs ]] && set -- install --no-initramfs
  command -v plymouth-set-default-theme >/dev/null || fail "plymouth is not installed"
  for f in "${FILES[@]}"; do [[ -f $HERE/$f ]] || fail "missing $f"; done
  sudo install -d -m 0755 "$DEST"
  for f in "${FILES[@]}"; do sudo install -m 0644 "$HERE/$f" "$DEST/$f"; done
  sudo sed -i "s|^ImageDir=.*|ImageDir=$DEST|; s|^ScriptFile=.*|ScriptFile=$DEST/$NAME.script|" "$DEST/$NAME.plymouth"
  if ! grep -q "^$MARK" "$CONF" 2>/dev/null; then
    sudo cp -a "$CONF" "$CONF.gs-backup" 2>/dev/null || true
    sudo sed -i "/^\[Daemon\]/a $MARK=1 keeps the theme's images sharp (install.sh remove takes it out)\nDeviceScale=1" "$CONF"
  fi
  sudo plymouth-set-default-theme "$NAME"
  mkdir -p "$(dirname "$HOOK")"
  printf '#!/bin/bash\n# gs-plymouth: report when an update selected another boot screen\n[[ $(plymouth-set-default-theme 2>/dev/null) == %s ]] || notify-send -u normal "Boot screen" "The Gehrmann Solutions boot screen is no longer selected. Install it again: %s"\n' \
    "$NAME" "$HERE/install.sh" >"$HOOK"
  rebuild "${2:-}"
  say "installed; the next boot shows it" ;;
remove)
  sudo sed -i "/^$MARK/,+1d" "$CONF"
  sudo plymouth-set-default-theme omarchy
  rm -f "$HOOK"
  rebuild "${2:-}"
  say "removed; Omarchy's boot screen is selected (the files stay in $DEST)" ;;
status)
  say "selected: $(current); DeviceScale: $(grep -m1 '^DeviceScale' "$CONF" 2>/dev/null || echo unset)" ;;
*)
  sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'; exit 2 ;;
esac
