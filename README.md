# Gehrmann Solutions — Omarchy theme

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
- `4-gs-logo.png` — the GS (Gehrmann Solutions) cloud/circuit logo, bold
  navy fill with a white outline, centered on a navy vignette
- `5-gs-logo-inverted.png` — background 4's shapes inverted (white fill,
  bold navy `#1c2d63` outline), for bright/light contexts
- `6-gs-logo-brightblue.png` — background 4's shapes with the bright
  accent blue `#2e3eff` fill instead of bold navy
- `7-gs-logo-brightblue.png` — background 5's shapes with the bright
  accent blue fill instead of white
- `8-gs-logo-glow.png` — background 4's look plus a soft blue glow,
  dead-centered (currently active)

All are centroid-corrected, not bounding-box-centered — the source art has
a slight asymmetric protrusion that makes naive bbox centering look off.

Cycle with `omarchy theme bg next`, or jump straight to one with
`omarchy theme bg set <path>`. After adding/changing background files,
`omarchy theme refresh && omarchy theme bg cache` — Omarchy snapshots the
theme folder at apply time, so the background switcher won't see new files
until that snapshot refreshes.

## Extras beyond the theme system

These aren't part of Omarchy's theme format, so `omarchy theme install` won't
apply them automatically — they're tracked here for backup/reference, with
manual install steps:

- `backgrounds/5-gs-logo-inverted.png` — inverted logo (white fill, bold navy
  `#1c2d63` outline) for bright backgrounds, same scale/position as background 4.
- `branding/gehrmann-logo.png` — transparent-background logo (navy fill,
  white outline), used on the lock screen.
- `lock-plugin/` — a clone of the `omarchy.lock` shell plugin with the logo
  added above the password field. Install with:
  ```bash
  cp -r lock-plugin ~/.config/omarchy/plugins/mg.lock
  cp branding/gehrmann-logo.png ~/.config/omarchy/branding/gehrmann-logo.png
  # then add to ~/.config/omarchy/shell.json:
  #   "plugins": [{"id": "mg.lock"}], "disabledPlugins": ["omarchy.lock"]
  omarchy restart shell
  ```
- `branding/screensaver.txt` — circuit-art ASCII rendition of the logo
  (generated with `omarchy transcode ascii`), replacing Omarchy's default
  screensaver content. ttfx still supplies the animated reveal effects
  (random each cycle) — only the artwork changed. Install with:
  ```bash
  cp branding/screensaver.txt ~/.config/omarchy/branding/screensaver.txt
  ```
  The original Omarchy default is backed up at
  `~/.config/omarchy/branding/screensaver.txt.orig-omarchy-backup`.

## Related, but not in this repo

A second, custom generative screensaver (circuit traces growing from the
logo, HTML5 canvas + Chromium kiosk, triggered via Omarchy's idle IPC since
`swayidle` doesn't get a working signal on this Hyprland build) lives
separately at `~/Nextcloud/GS-Logo/screensaver/` — not part of this git
repo since it's not an Omarchy theme-format asset. See its own README for
what it is and how to install it on another machine. `~/Nextcloud/GS-Logo/`
also has the traceable vector source (`gs-logo.svg`) for the logo used
throughout this theme.

## Repo layout

This theme directory is a self-contained git repo, which is Omarchy's
native theme distribution format. It lives in three places, each with a
different role:

- `~/Work/tries/gehrmann-solutions-theme` — **canonical** copy. Edit here.
- `~/.config/omarchy/themes/gehrmann-solutions` — the **live** copy Omarchy
  actually reads/applies. Remote `origin` points at the canonical copy.
- `https://github.com/GehrmannSolutions/Omarchy` — public monorepo, this
  theme lives under `Themes/gehrmann-solutions/` on branch `main`, merged
  in via `git subtree` (full history preserved). A local working clone of
  the monorepo is kept at `~/Work/tries/omarchy`.

**Import (on any Omarchy machine):**

```bash
omarchy theme install /path/to/gehrmann-solutions-theme   # local path
# or, from GitHub (sparse — pulls just this theme's history+prefix):
omarchy theme install https://github.com/GehrmannSolutions/Omarchy.git
```

**Remove:**

```bash
omarchy theme remove gehrmann-solutions
```

## Workflow: editing and publishing

1. Edit and commit in the canonical copy:
   ```bash
   cd ~/Work/tries/gehrmann-solutions-theme
   git add -A && git commit -m "describe the change"
   ```
2. Pull into the live theme so Omarchy picks it up (the live copy's `origin`
   already points at the canonical copy; can't push directly into it since
   its branch is checked out there):
   ```bash
   cd ~/.config/omarchy/themes/gehrmann-solutions
   git pull origin master
   omarchy theme refresh && omarchy theme bg cache
   ```
3. Publish to the public GitHub monorepo:
   ```bash
   cd ~/Work/tries/omarchy
   git subtree pull --prefix=Themes/gehrmann-solutions gehrmann-solutions-theme master
   git push origin main
   ```
