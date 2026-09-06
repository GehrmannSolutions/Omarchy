"""Named, on-disk configuration profiles for timeBuzzer-based control scripts.

A profile is just an arbitrary JSON-serializable dict - a control script
decides what the keys mean (e.g. which action a rotate/click maps to). This
lets a script save a named configuration, list what's available, and switch
which one is "active" between runs.
"""

from __future__ import annotations

import json
from pathlib import Path

DEFAULT_DIR = Path.home() / ".config" / "timebuzzer" / "profiles"
ACTIVE_FILE = Path.home() / ".config" / "timebuzzer" / "active_profile"


class ProfileStore:
    def __init__(self, directory: Path | str = DEFAULT_DIR):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _path(self, name: str) -> Path:
        return self.directory / f"{name}.json"

    def save(self, name: str, config: dict) -> None:
        self._path(name).write_text(json.dumps(config, indent=2, sort_keys=True))

    def load(self, name: str) -> dict:
        try:
            return json.loads(self._path(name).read_text())
        except FileNotFoundError:
            raise KeyError(f"no such profile: {name!r}") from None

    def delete(self, name: str) -> None:
        self._path(name).unlink(missing_ok=True)

    def rename(self, old_name: str, new_name: str) -> None:
        if old_name == new_name:
            return
        if new_name in self.list():
            raise KeyError(f"profile already exists: {new_name!r}")
        config = self.load(old_name)
        was_active = self.active == old_name
        self.save(new_name, config)
        self.delete(old_name)
        if was_active:
            self.active = new_name

    def list(self) -> list[str]:
        return sorted(p.stem for p in self.directory.glob("*.json"))

    @property
    def active(self) -> str | None:
        try:
            return ACTIVE_FILE.read_text().strip() or None
        except FileNotFoundError:
            return None

    @active.setter
    def active(self, name: str | None) -> None:
        ACTIVE_FILE.parent.mkdir(parents=True, exist_ok=True)
        if name is None:
            ACTIVE_FILE.unlink(missing_ok=True)
        else:
            ACTIVE_FILE.write_text(name)
