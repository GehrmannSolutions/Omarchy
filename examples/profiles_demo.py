#!/usr/bin/env python3
"""Shows the profile workflow: save a named config, list what's saved, and
run with whichever profile is currently active.

Usage:
    profiles_demo.py save <name>   save an example config and activate it
    profiles_demo.py list          list saved profiles, '*' marks the active one
    profiles_demo.py               listen using the active profile
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from timebuzzer import ProfileStore, TimeBuzzer


def main() -> None:
    store = ProfileStore()

    if len(sys.argv) >= 3 and sys.argv[1] == "save":
        name = sys.argv[2]
        store.save(name, {"rotate_action": "volume", "click_action": "play_pause"})
        store.active = name
        print(f"saved profile {name!r} and made it active")
        return

    if len(sys.argv) >= 2 and sys.argv[1] == "list":
        for name in store.list():
            marker = "*" if name == store.active else " "
            print(f"{marker} {name}")
        return

    name = store.active
    if not name:
        print("no active profile - create one first: profiles_demo.py save <name>")
        return
    config = store.load(name)
    print(f"active profile: {name} -> {config}")

    tb = TimeBuzzer(
        on_rotate=lambda delta: print(f"[{name}] rotate {delta:+d} ({config.get('rotate_action')})"),
        on_click=lambda: print(f"[{name}] click ({config.get('click_action')})"),
    )
    print(f"listening on {tb.device} - Ctrl+C to stop")
    try:
        tb.run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
