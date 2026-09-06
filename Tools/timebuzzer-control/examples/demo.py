#!/usr/bin/env python3
"""Prints every timeBuzzer event as it happens - run this to try the toolkit
or to sanity-check a device after a firmware/hardware change."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from timebuzzer import TimeBuzzer


def main() -> None:
    tb = TimeBuzzer(
        on_rotate=lambda delta: print(f"rotate {delta:+d}"),
        on_touch=lambda active: print("touch" if active else "release"),
        on_click=lambda: print("click"),
    )
    print(f"listening on {tb.device} - Ctrl+C to stop")
    try:
        tb.run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
