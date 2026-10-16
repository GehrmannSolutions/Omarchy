# Gehrmann Solutions Omarchy themes — source

This folder is the source of two [Omarchy](https://omarchy.org) themes in the colours of
[gehrmann.solutions](https://gehrmann.solutions). They are published as their own repositories,
because `omarchy theme install` clones a whole repository as one theme:

| Theme | Install |
|---|---|
| [Gehrmann Solutions](https://github.com/GehrmannSolutions/omarchy-gehrmann-solutions-theme) (dark) | `omarchy theme install https://github.com/GehrmannSolutions/omarchy-gehrmann-solutions-theme.git` |
| [Gehrmann Solutions Light](https://github.com/GehrmannSolutions/omarchy-gehrmann-solutions-light-theme) | `omarchy theme install https://github.com/GehrmannSolutions/omarchy-gehrmann-solutions-light-theme.git` |

## Layout

| Path | What |
|---|---|
| `source/gs-logo.svg` | the GS cloud-and-circuit logo as a layered SVG (background, glow, outline, infill); traced with potrace, so the outline has a sketched, hand-drawn line |
| `source/gs-logo.png` | the original two-tone raster logo (white outline, navy infill) |
| `source/sunburst-*.jpg` | the website's dot sunburst graphic, navy and white |
| `tools/build.sh` | builds every image of both themes: backgrounds, `unlock.png`, `preview-unlock.png` |
| `tools/logo-variant.py` | recolours the SVG's layers for one variant |
| `tools/centroid.py` | finds the logo's visual centre (its cloud reaches further right than left) |
| `extras/gs-lock-logo` | optional: the theme's logo on the lock screen (see the themes' READMEs) |
| `extras/screensaver.txt` | optional: the logo as text art for Omarchy's screensaver |

## Building

```bash
git clone https://github.com/GehrmannSolutions/omarchy-gehrmann-solutions-theme.git
git clone https://github.com/GehrmannSolutions/omarchy-gehrmann-solutions-light-theme.git
Themes/gehrmann-solutions/tools/build.sh omarchy-gehrmann-solutions-theme omarchy-gehrmann-solutions-light-theme
```

Needs `rsvg-convert` (librsvg), `magick` (ImageMagick 7) and Python 3. `LOGO_SOURCE=raster` builds
the logos from the original raster instead of the SVG. The palettes (`colors.toml`), the lock
field colours (`shell.lock.toml`), the READMEs and the previews (`preview.png`, a desktop
screenshot) live in the theme repositories themselves.

## Licence

The scripts here are MIT licensed; the Gehrmann Solutions name and logo and every image showing
them are © Gehrmann Solutions, all rights reserved (see the themes' LICENSE).
