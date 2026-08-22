# Gehrmann — Omarchy theme

A dark Omarchy theme built from the real brand assets of
[gehrmann.solutions](https://gehrmann.solutions): deep navy backgrounds,
a single vivid electric-blue accent, and the site's own radial halftone
"sunburst" graphic reused as wallpaper.

## Palette

| Role        | Hex       | Source |
|-------------|-----------|--------|
| Background  | `#192031` | site's dark section / footer background (`--dark-blue`) |
| Accent      | `#2e3eff` | site's bright link/CTA blue (`--blue-bright`) |
| Accent (alt)| `#222fd3` | site's button/pattern blue (`--blue-dark`) |
| Foreground  | `#f5f6fa` | near-white, mirrors the site's white sections |

Terminal ANSI colors are desaturated, cool-toned hues (coral red, gold,
mint green, sky cyan, violet) rather than pure brand blue everywhere, so
diffs/test output/syntax highlighting stay readable — see `colors.toml`.

## Backgrounds

Generated from the site's own `pattern.svg` (a radial halftone dot-burst,
`#222FD3` in the original):

- `1-sunburst-navy.jpg` — navy background, bright-blue burst
- `2-sunburst-white.jpg` — white background, navy burst (mirrors the
  site's alternating light sections)
- `3-navy-plain.jpg` — plain navy gradient, no pattern
- `4-gs-logo.png` — the GS (Gehrmann Solutions) cloud/circuit logo,
  recolored as a navy/accent-blue duotone with a soft glow, centered on
  a navy vignette (currently active)

Cycle with `omarchy theme bg next`, or jump straight to one with
`omarchy theme bg set <path>`.

## Export / Import

This theme directory is a self-contained git repo, which is Omarchy's
native theme distribution format.

**Export (from this machine):** already tracked here at
`~/.config/omarchy/themes/gehrmann`. A synced copy lives in
`~/Nextcloud/omarchy-gehrmann-theme`.

**Import (on any Omarchy machine):**

```bash
omarchy theme install /path/to/omarchy-gehrmann-theme   # local path (e.g. synced Nextcloud folder)
# or, if pushed to a remote:
omarchy theme install https://github.com/<you>/omarchy-gehrmann-theme.git
```

**Remove:**

```bash
omarchy theme remove gehrmann
```

## Updating the Nextcloud copy

The Nextcloud folder is a git clone of this repo, with its working tree
checked out (so Nextcloud can sync the files) — that means it can only be
*pulled into*, not pushed to directly. After changing anything in the live
theme, sync the Nextcloud copy by pulling from it:

```bash
cd ~/.config/omarchy/themes/gehrmann
git add -A && git commit -m "describe the change"

cd ~/Nextcloud/omarchy-gehrmann-theme
git pull   # remote "live" already points at ~/.config/omarchy/themes/gehrmann
```
