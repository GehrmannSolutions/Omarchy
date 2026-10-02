# Arch Linux ARM (Omarchy) on Apple Silicon — GEH-37

Goal: a fully working Arch Linux ARM environment on Apple M\* Macs, ideally
running Omarchy so the themes/tools in this repo apply.

State of the ecosystem (verified 2026-10-02):

| Your Mac | Recommended path | Status |
|---|---|---|
| **M1 / M2** (incl. Pro/Max/Ultra) | **Bare metal**: Asahi Alarm + `omarchy-mac` dual-boot alongside macOS | Working today. GPU, Wi‑Fi, Touch ID, external displays via USB‑C, disk encryption. |
| **M3 / M4 / M5** | **VM**: native aarch64 Omarchy in UTM (free) or Parallels (better graphics) | Working today with caveats (see below). Asahi has no M3+ support yet — no bare-metal option. |
| Any M\* chip, vanilla Arch (no Omarchy) | Arch Linux ARM aarch64 VM in UTM | Trivial; UTM gallery has ALARM images. |

The helper script in this directory, [`omarchy-apple-silicon.sh`](omarchy-apple-silicon.sh),
detects your chip and walks you through the right path. Run it **on the Mac**:

```bash
bash Tools/arch-arm-apple-silicon/omarchy-apple-silicon.sh
```

---

## Path A — Bare metal on M1/M2 (Asahi Alarm + omarchy-mac)

This is real Arch Linux ARM booting natively next to macOS, using Asahi
Linux's partitioner and Apple Silicon kernel work. Nothing in macOS is
touched; a boot menu lets you pick macOS or Linux at startup.

**Prerequisites**
- M1/M2-family Mac (M3+ not supported — use Path B)
- macOS 15 or later, recent Time Machine backup
- ≥ 50 GB free on the internal SSD (100 GB recommended)

**Install (~15 min, 3 automatic reboots)**

1. From macOS Terminal, run the Asahi Alarm installer and choose
   **Asahi Alarm Minimal (BTRFS)**, allocating ≥ 50 GB:

   ```bash
   curl https://asahi-alarm.org/installer-bootstrap.sh | sh
   ```

2. Reboot into the new Arch system, log in as `root` / `root`, and bring up
   Wi‑Fi with `nmtui`.

3. Run the Omarchy Mac setup (prompts for hostname, user, password,
   encryption — encryption is on by default):

   ```bash
   curl -fsSL https://raw.githubusercontent.com/omarchy-mac/omarchy-mac/quattro/bin/omarchy-mac-setup | bash
   ```

   Useful flags: `--no-encrypt`, `--status`, `--step <name>` (re-run a step).

**Known issues**
- SSH: Omarchy enables a default-deny firewall that never opens port 22.
  Run `omarchy-setup-security-sshd` afterwards if you want SSH in.
- If you ever land in `grub rescue>`: `/boot` must live on the EFI partition
  before enabling encryption — see the omarchy-mac README.
- Rollback: `omarchy snapshot restore` with the `@fresh` (pre-Omarchy) or
  `@factory` (post-install baseline) BTRFS snapshots.
- Uninstall: no automatic uninstaller. Remove the Linux partitions from
  macOS and expand the macOS container per the Asahi partitioning
  cheatsheet — careful work, follow it exactly.

There is also the official **Omarchy M** effort (announced Sept 2026,
<https://omarchy.org/news/2026/09/introducing-omarchy-m/>): a native Mac
installer app plus a "Try Omarchy" app that runs Omarchy hardware-accelerated
inside macOS without partitioning. M1/M2 today, M3–M5 in development. Still
preview-quality as of early Oct 2026; the Asahi Alarm + omarchy-mac path above
is the proven route right now, but Omarchy M is worth watching — once it ships
a polished release it will likely become the recommended path.

## Path B — VM on M3/M4/M5 (or if you don't want to repartition)

Native aarch64 Omarchy inside a VM. Two options:

**B1. UTM (free) — prebuilt image or one-script build**

- Prebuilt: download `omarchy-arm-utm-v2.zip` (~3.6 GB) from
  <https://archive.org/details/omarchy-arm-utm>, unzip, open the `.utm`
  bundle in UTM, boot. (Community-built image — treat it accordingly; build
  it yourself below if you'd rather not trust a third-party image.)
- Build it yourself (~1 h on an M3 Max, 8 resumable phases):

  ```bash
  brew install --cask utm
  git clone https://github.com/ggalancs/omarchy-arm-utm.git
  cd omarchy-arm-utm
  ./build-omarchy-arm.sh
  ```

  UTM caveats: no GL acceleration (software rendering via
  `LIBGL_ALWAYS_SOFTWARE=1`), single monitor, set resolution at boot (runtime
  changes white-screen), and macOS swallows Cmd so the image maps **Option (⌥)
  as SUPER**. Fine for daily terminal/editor work; not for GPU-heavy use.
  Daily-driver tuning notes: <https://github.com/dchersey/omarchy-apple-silicon-utm>.

**B2. Parallels Desktop (paid) — better graphics**

<https://github.com/vincenzopalazzo/omarchy-parallels> repackages the official
try-omarchy guest into a bootable Parallels VM and also publishes a live ISO
(`omarchy-arm-*-aarch64.iso`) usable in Parallels/UTM/QEMU as an installer CD.

**Vanilla Arch Linux ARM (no Omarchy)**: in UTM, create an aarch64 UEFI VM
from the UTM gallery's Arch Linux ARM image, or boot an aarch64 installer ISO
and install ALARM normally.

## Sources

- Omarchy M announcement: <https://omarchy.org/news/2026/09/introducing-omarchy-m/>
- omarchy-mac (bare metal M1/M2): <https://github.com/omacom/omarchy-mac>
- Asahi Alarm installer: <https://asahi-alarm.org>
- One-script UTM build discussion: <https://github.com/omacom/omarchy/discussions/7956>
- UTM build repo: <https://github.com/ggalancs/omarchy-arm-utm> · prebuilt image: <https://archive.org/details/omarchy-arm-utm>
- UTM daily-driver fixes: <https://github.com/dchersey/omarchy-apple-silicon-utm>
- Parallels repack + live ISO: <https://github.com/vincenzopalazzo/omarchy-parallels>
- Asahi device support (M1/M2 only): <https://asahilinux.org/fedora/#device-support>
