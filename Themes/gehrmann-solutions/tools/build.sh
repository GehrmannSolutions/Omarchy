#!/usr/bin/env bash
# Build the images of both Gehrmann Solutions Omarchy themes from source/:
#   backgrounds/, unlock.png (Plymouth boot / disk unlock logo), preview-unlock.png and
#   extras/plymouth/ (the animated boot screen, optional).
# preview.png is a real desktop screenshot: tools/preview.sh, with the theme installed and active.
#
# usage: tools/build.sh DARK_THEME_DIR LIGHT_THEME_DIR
# Needs: rsvg-convert (librsvg), magick (ImageMagick 7), python3.
set -euo pipefail

HERE=$(cd "$(dirname "$0")/.." && pwd)
SRC=$HERE/source
DARK=${1:?dark theme dir}
LIGHT=${2:?light theme dir}
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

W=3840 H=2160            # 16:9 4K; Omarchy fills the screen (cover), so other ratios crop the edges
LOGO_SHARE=0.70          # the logo's 1024-unit SVG box as a share of the background height; the shapes fill ~80 % of it
MARGIN=128               # logo-variant.py viewBox margin, of 1024 units
UNLOCK_H=440             # unlock.png height in pixels (Plymouth draws it unscaled, centred)

# brand colours (gehrmann.solutions CSS)
NAVY=#192031 NAVY_DARK=#12172a NAVY_LIGHT=#222c4b BOLD_NAVY=#1c2d63
BLUE=#2e3eff WHITE=#ffffff
PAPER=#f5f6fa PAPER_EDGE=#e4e7f0

need() { command -v "$1" >/dev/null || { echo "build.sh: $1 is missing" >&2; exit 1; }; }
need rsvg-convert; need magick; need python3

# logo NAME OUTLINE INFILL [GLOW OPACITY] -> $TMP/NAME.png at background scale, transparent.
# LOGO_SOURCE=svg (default): source/gs-logo.svg, a potrace trace with a sketched, hand-drawn
# outline and a real blur glow (the look of these themes). LOGO_SOURCE=raster: source/gs-logo.png,
# the original two-tone artwork (white outline, navy infill), recoloured by its lightness.
logo() {
  local name=$1 outline=$2 infill=$3 glow=${4:-} opacity=${5:-0.75} px pad sigma
  px=$(python3 -c "print(round($H * $LOGO_SHARE))")
  if [[ ${LOGO_SOURCE:-svg} == svg ]]; then
    local args=()
    [[ -n $glow ]] && args=(--glow "$glow" --glow-opacity "$opacity")
    python3 -I "$HERE/tools/logo-variant.py" "$SRC/gs-logo.svg" "$TMP/$name.svg" \
      --outline "$outline" --infill "$infill" --margin $MARGIN "${args[@]}"
    rsvg-convert -h "$(python3 -c "print(round($px * (1024 + 2 * $MARGIN) / 1024))")" "$TMP/$name.svg" -o "$TMP/$name.png"
    return
  fi
  pad=$(( px / 8 ))
  sigma=$(python3 -c "print(round($px * 16 / 1024, 1))")
  px=$(( px * 8 / 10 ))   # the raster is trimmed to the shapes, the SVG box is not
  magick "$SRC/gs-logo.png" -trim +repage -filter Lanczos -resize "x$px" -bordercolor none -border "$pad" "$TMP/$name-src.png"
  # lightness 0 at the navy infill, 1 at the white outline: the outline/infill mix
  magick "$TMP/$name-src.png" -alpha off -colorspace gray -level 20%,93% "$TMP/$name-mask.png"
  magick "$TMP/$name-src.png" \( +clone -alpha off -fill "$infill" -colorize 100 \) \
    \( +clone -fill "$outline" -colorize 100 \) "$TMP/$name-mask.png" -delete 0 -composite \
    "$TMP/$name-src.png" -compose CopyOpacity -composite "$TMP/$name.png"
  if [[ -n $glow ]]; then
    magick "$TMP/$name-src.png" -alpha extract -blur 0x"$sigma" -evaluate multiply "$opacity" \
      \( +clone -fill "$glow" -colorize 100 \) +swap -alpha off -compose CopyOpacity -composite \
      "$TMP/$name.png" -compose Over -composite "$TMP/$name.png"
  fi
}

# The centroid of the logo shapes (no glow), as pixel offsets from the image centre.
logo noglow '#ffffff' '#ffffff'  # shapes only: outline and infill alike
read -r CX CY < <(magick "$TMP/noglow.png" -alpha extract -resize 512x512 pgm:- | python3 -I "$HERE/tools/centroid.py")
LOGO_PX=$(magick identify -format '%w' "$TMP/noglow.png")
DX=$(python3 -c "print(round((0.5 - $CX) * $LOGO_PX))")
DY=$(python3 -c "print(round((0.5 - $CY) * $LOGO_PX))")
offset() { printf '%+d%+d' "$DX" "$DY"; }

# canvas NAME CENTRE EDGE -> radial gradient, dithered so it does not band
canvas() {
  magick -size ${W}x${H} "radial-gradient:$2-$3" -seed 1 -attenuate 0.6 +noise Uniform -depth 8 "$TMP/$1.png"
}

# place BACKGROUND LOGO OUT
place() {
  magick "$TMP/$1.png" "$TMP/$2.png" -gravity center -geometry "$(offset)" -composite \
    -strip -quality 90 -sampling-factor 4:4:4 "$3"
}

# unlock LOGO OUT: trimmed logo (glow kept), UNLOCK_H high, transparent
unlock() {
  magick "$TMP/$1.png" -trim +repage -resize x$UNLOCK_H -strip "$2"
}

# preview_unlock UNLOCK BG FG OUT: the Plymouth screen as omarchy.script lays it out
preview_unlock() {
  local logo=$1 bg=$2 fg=$3 out=$4 lh ey
  lh=$(magick identify -format '%h' "$logo")
  ey=$(( (1080 - lh) / 2 + lh + 40 ))
  magick -size 1920x1080 "xc:$bg" \
    "$logo" -gravity north -geometry "+0+$(( (1080 - lh) / 2 ))" -composite \
    -fill none -stroke "$fg" -strokewidth 2 -draw "roundrectangle 817,$ey 1103,$((ey + 48)) 6,6" \
    -fill "$fg" -stroke none -draw "roundrectangle 771,$((ey + 20)) 799,$((ey + 42)) 3,3" \
    -fill none -stroke "$fg" -strokewidth 3 -draw "arc 775,$((ey + 6)) 795,$((ey + 30)) 180,360" \
    -fill "$fg" -stroke none \
    -draw "circle 840,$((ey + 24)) 843,$((ey + 24))" -draw "circle 852,$((ey + 24)) 855,$((ey + 24))" \
    -draw "circle 864,$((ey + 24)) 867,$((ey + 24))" -draw "circle 876,$((ey + 24)) 879,$((ey + 24))" \
    -strip "$out"
}

# plymouth OUT OUTLINE INFILL GLOW BG FG ACCENT GLOW_LO GLOW_HI: the boot screen theme (extras/plymouth)
# with high-resolution images the script scales down: the logo's shapes and its glow as separate
# layers (the glow breathes), and the dialog images at four times Omarchy's sizes.
plymouth() {
  local out=$1 outline=$2 infill=$3 glow=$4 bg=$5 fg=$6 accent=$7 lo=$8 hi=$9 rgb
  mkdir -p "$out"
  python3 -I "$HERE/tools/logo-variant.py" "$SRC/gs-logo.svg" "$TMP/ply-shapes.svg" --outline "$outline" --infill "$infill" --margin $MARGIN
  python3 -I "$HERE/tools/logo-variant.py" "$SRC/gs-logo.svg" "$TMP/ply-glow.svg" --outline "$outline" --infill "$infill" \
    --glow "$glow" --glow-opacity 1 --glow-only --margin $MARGIN
  rsvg-convert -h 1280 "$TMP/ply-shapes.svg" -o "$out/logo-shapes.png"
  rsvg-convert -h 1280 "$TMP/ply-glow.svg" -o "$out/logo-glow.png"
  magick -size 1144x192 xc:none -fill none -stroke "$fg" -strokewidth 8 -draw "roundrectangle 4,4 1139,187 24,24" "$out/entry.png"
  magick -size 336x384 xc:none -fill "$fg" -draw "roundrectangle 0,160 335,383 36,36" \
    -fill none -stroke "$fg" -strokewidth 44 -draw "arc 62,24 274,260 180,360" \
    -stroke none -fill "$fg" -draw "rectangle 40,142 84,180" -draw "rectangle 252,142 296,180" "$out/lock.png"
  magick -size 56x56 xc:none -fill "$fg" -draw "circle 28,28 28,2" "$out/bullet.png"
  magick -size 1200x40 xc:none -fill none -stroke "$fg" -strokewidth 4 -draw "roundrectangle 2,2 1197,37 18,18" "$out/progress_box.png"
  magick -size 1200x40 xc:none -fill "$accent" -draw "roundrectangle 0,0 1199,39 20,20" "$out/progress_bar.png"
  for f in "$out"/*.png; do magick "$f" -strip "$f"; done
  rgb=$(python3 -c "h='$bg'.lstrip('#'); print(', '.join('%.3f' % (int(h[i:i+2], 16) / 255) for i in (0, 2, 4)))")
  local trgb; trgb=$(python3 -c "h='$fg'.lstrip('#'); print(', '.join('%.3f' % (int(h[i:i+2], 16) / 255) for i in (0, 2, 4)))")
  sed -e "s/@BG@/$rgb/" -e "s/@TEXT@/$trgb/" -e "s/@GLOW_LO@/$lo/g" -e "s/@GLOW_HI@/$hi/g" \
    "$HERE/extras/plymouth/gehrmann-solutions.script.in" >"$out/gehrmann-solutions.script"
  ! grep -q '@[A-Z_]*@' "$out/gehrmann-solutions.script" || { echo "build.sh: unreplaced placeholder in the Plymouth script" >&2; exit 1; }
  install -m 0644 "$HERE/extras/plymouth/gehrmann-solutions.plymouth" "$out/"
  install -m 0755 "$HERE/extras/plymouth/install.sh" "$out/"
}

mkdir -p "$DARK/backgrounds" "$LIGHT/backgrounds"
rm -f "$DARK"/backgrounds/* "$LIGHT"/backgrounds/*

# --- dark: navy, white outline -------------------------------------------------------
canvas navy "$NAVY_LIGHT" "$NAVY_DARK"
logo d-glow "$WHITE" "$BOLD_NAVY" "$BLUE" 0.75
logo d-plain "$WHITE" "$BOLD_NAVY"
logo d-blue "$WHITE" "$BLUE"
place navy d-glow "$DARK/backgrounds/1-gs-logo-glow.jpg"
place navy d-plain "$DARK/backgrounds/2-gs-logo.jpg"
place navy d-blue "$DARK/backgrounds/3-gs-logo-brightblue.jpg"
cp "$SRC/sunburst-navy.jpg" "$DARK/backgrounds/4-sunburst-navy.jpg"
magick "$TMP/navy.png" -quality 92 "$DARK/backgrounds/5-navy-plain.jpg"
unlock d-glow "$DARK/unlock.png"
preview_unlock "$DARK/unlock.png" "$NAVY" "#f5f6fa" "$DARK/preview-unlock.png"
plymouth "$DARK/extras/plymouth" "$WHITE" "$BOLD_NAVY" "$BLUE" "$NAVY" "#f5f6fa" "$BLUE" 0.12 1.0

# --- light: paper, the dark theme's logo inverted (navy outline, white fill) ----------
canvas paper "$WHITE" "$PAPER_EDGE"
logo l-inv "$BOLD_NAVY" "$WHITE"
logo l-blue "$BOLD_NAVY" "$BLUE"
logo l-glow "$BOLD_NAVY" "$WHITE" "$BLUE" 0.5
place paper l-inv "$LIGHT/backgrounds/1-gs-logo-inverted.jpg"
place paper l-blue "$LIGHT/backgrounds/2-gs-logo-brightblue.jpg"
place paper l-glow "$LIGHT/backgrounds/3-gs-logo-glow.jpg"
cp "$SRC/sunburst-white.jpg" "$LIGHT/backgrounds/4-sunburst-white.jpg"
magick "$TMP/paper.png" -quality 92 "$LIGHT/backgrounds/5-paper-plain.jpg"
unlock l-blue "$LIGHT/unlock.png"
preview_unlock "$LIGHT/unlock.png" "$PAPER" "$NAVY" "$LIGHT/preview-unlock.png"
plymouth "$LIGHT/extras/plymouth" "$BOLD_NAVY" "$BLUE" "$BLUE" "$PAPER" "$NAVY" "$BLUE" 0.05 0.7

# --- extras, the same in both themes --------------------------------------------------------
for theme in "$DARK" "$LIGHT"; do
  mkdir -p "$theme/extras"
  install -m 0755 "$HERE/extras/gs-lock-logo" "$theme/extras/gs-lock-logo"
  install -m 0644 "$HERE/extras/screensaver.txt" "$theme/extras/screensaver.txt"
done

echo "built: $(ls "$DARK/backgrounds" | wc -l) + $(ls "$LIGHT/backgrounds" | wc -l) backgrounds, unlock + preview-unlock for both;" \
  "logo centroid offset $(offset) px"
