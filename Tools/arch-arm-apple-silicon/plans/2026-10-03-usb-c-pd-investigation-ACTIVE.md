# USB-C ports on the MacBook Air M3 (Omarchy / Asahi) — investigation

**Status: ACTIVE.** Diagnosis done, no fix applied yet.

**Owner:** Fay (laptop session). **Created:** 2026-10-03.

## Goal

Make the USB-C ports work on the M3 MacBook Air running Omarchy on Arch Linux
ARM, so that USB devices, USB-C storage, a dock and DisplayPort over USB-C
become usable.

## What was checked (read-only, 2026-10-03)

1. `/sys/bus/usb/devices/` is empty. No root hub is created.
2. `/sys/class/typec/` is empty. No Type-C port is registered with the kernel.
3. `dwc3-apple` is bound to `702280000.usb` and `b02280000.usb`, and no xHCI
   host appears.
4. The PD controllers `usb-pd@a` and `usb-pd@c` have compatible
   `apple,sn201202x`. Their SPMI devices `1-0a` and `1-0c` have no driver.
5. The kernel module `tps6598x` (`tipd`) matches only `ti,tps6598x`,
   `ti,tps25750` and `apple,cd321x`. It does not match `sn201202x`.
6. Kernel log: `Fixed dependency cycle(s)` between the connectors and the USB and
   PHY nodes at boot. Expected, not the failure.

Commands used, for reproducing the check:

```
ls /sys/bus/usb/devices/
ls /sys/class/typec/
readlink /sys/bus/platform/devices/702280000.usb/driver
ls /sys/bus/spmi/devices/
for x in /sys/bus/spmi/devices/*; do echo "$(basename $x) $(basename $(readlink $x/driver 2>/dev/null))"; done
modinfo tps6598x | grep alias
journalctl -k -b | grep -iE 'usb-pd|typec|sn2012'
```

## Open questions

- Does an upstream or Asahi kernel have `apple,sn201202x` support? Check the
  Asahi kernel tree and the upstream `drivers/usb/typec/tipd` history.
- Is the `sn201202x` controller register-compatible with `cd321x`? If yes, a
  compatible-string patch may be enough. If no, a new driver is needed.
- Can a device-tree overlay change the compatible string, or is a kernel rebuild
  required?

## Options (not yet decided)

1. **Upstream or Asahi patch**: find or write a compatible-string addition for
   `sn201202x` in the `tipd` driver. Rebuild the kernel. Most durable.
2. **Device-tree change**: test whether the `usb-pd` nodes can be given the
   `cd321x` compatible string via an overlay. Quick to test, but it may not work
   if the register map differs.
3. **Accept the gap and report upstream**: write up the finding for the Asahi
   project. Ports stay broken until someone else fixes them.

## Update 2026-10-03: research result

- A driver for `apple,sn201202x` exists as a v2 patch series (27 Jul 2026, LKML
  2607.3). It is not merged in Asahi or mainline. See
  `project-usb-c-pd-controller.md`.
- The fix is therefore to build a kernel with the three patches applied.
  Upstream merge is the long-term path.

## Recommendation

Start with a search for an existing Asahi or upstream fix (option 1), since that
is the cheapest answer if one exists. Then decide between option 2 and option 3.
Option 2 needs a reboot test after each change. The shared infra-change rules
(`../../../claude-memory/feedback_infra_change_approach.md`) apply: back up first.

## Next steps (proposed, not started)

1. Fetch the Asahi kernel source for 7.1.13.asahi3 and check it applies the
   three patches cleanly (dry run only, nothing built).
2. Install `bc` and `pahole`, prepare a build tree.
3. Build the module first (`make M=drivers/usb/typec/tipd`) and test loading it
   without rebooting.
4. Only if that works: build the full kernel, install it next to the current one,
   keep the current kernel as the GRUB fallback, reboot, verify with
   `/sys/class/typec` and `/sys/bus/usb/devices`.

## Checkpoint

Before any change to the device tree or the kernel: back up the current boot
setup and report the findings to Marius. Ask for a go-ahead before the first
modification.
