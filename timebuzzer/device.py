"""Driver for the timeBuzzer USB dial (Ideas in Logic GbR, VID 16d0 / PID 1170).

The device enumerates as a USB-MIDI class-compliant gadget (no vendor driver,
no HID) and shows up as an ALSA rawmidi port. Reverse engineered by capturing
the raw byte stream with `amidi -p hw:X,0,0 -d` while touching / turning /
clicking the dial. All events arrive as Control Change messages on MIDI
channel 12 (status byte 0xBB):

    CC 80 (rotate)  running 7-bit tick counter, wraps 0..127.
                    Turning clockwise increments it, counter-clockwise
                    decrements it, one step per detent.
    CC 81 (touch)   heartbeat sent every ~1.5s regardless of activity:
                    127 = not touched, 0 = finger resting on the dial.
    CC 82 (button)  sent only on the mechanical click, as a quick
                    127-then-0 pair (press, then release).

See CLAUDE.md in this project for how the capture was done.
"""

from __future__ import annotations

import re
import threading
from pathlib import Path
from typing import Callable

CHANNEL = 0x0B  # MIDI channel 12 (0-indexed 11)
CC_ROTATE = 80
CC_TOUCH = 81
CC_BUTTON = 82


def find_device() -> str:
    """Locate the timeBuzzer's ALSA rawmidi device node via /proc/asound."""
    for id_file in Path("/proc/asound").glob("card*/id"):
        if id_file.read_text().strip() == "timeBuzzer":
            card_index = re.sub(r"\D", "", id_file.parent.name)
            return f"/dev/snd/midiC{card_index}D0"
    raise FileNotFoundError(
        "timeBuzzer not found under /proc/asound - is it plugged in?"
    )


class TimeBuzzer:
    """Listens on the timeBuzzer's raw MIDI stream and fires callbacks.

    Usage:
        tb = TimeBuzzer(on_rotate=..., on_touch=..., on_click=...)
        tb.run()  # blocks, or tb.start()/tb.stop() for a background thread
    """

    def __init__(
        self,
        device: str | None = None,
        on_rotate: Callable[[int], None] | None = None,
        on_touch: Callable[[bool], None] | None = None,
        on_click: Callable[[], None] | None = None,
        on_button_down: Callable[[], None] | None = None,
        on_button_up: Callable[[], None] | None = None,
    ):
        self.device = device or find_device()
        self.on_rotate = on_rotate
        self.on_touch = on_touch
        self.on_click = on_click
        self.on_button_down = on_button_down
        self.on_button_up = on_button_up

        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._last_rotate: int | None = None
        self._last_touch: bool | None = None
        self._button_down_pending = False

    def start(self) -> None:
        """Run the read loop in a background thread."""
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)

    def run(self) -> None:
        """Run the read loop in the calling thread (blocks until stop())."""
        self._run()

    def _run(self) -> None:
        with open(self.device, "rb", buffering=0) as f:
            running_status: int | None = None
            while not self._stop.is_set():
                byte = f.read(1)
                if not byte:
                    continue
                b = byte[0]
                if b & 0x80:
                    running_status = b
                    if b >= 0xF0:
                        continue  # system message, not used by this device
                    data1 = f.read(1)[0]
                    data2 = f.read(1)[0]
                    self._dispatch(running_status, data1, data2)
                elif running_status is not None and running_status < 0xF0:
                    data2 = f.read(1)[0]
                    self._dispatch(running_status, b, data2)

    def _dispatch(self, status: int, data1: int, data2: int) -> None:
        if (status & 0xF0) != 0xB0 or (status & 0x0F) != CHANNEL:
            return
        controller, value = data1, data2

        if controller == CC_ROTATE:
            if self._last_rotate is not None:
                delta = (value - self._last_rotate + 64) % 128 - 64
                if delta and self.on_rotate:
                    self.on_rotate(delta)
            self._last_rotate = value

        elif controller == CC_TOUCH:
            active = value == 0
            if active != self._last_touch:
                self._last_touch = active
                if self.on_touch:
                    self.on_touch(active)

        elif controller == CC_BUTTON:
            if value == 0x7F:
                self._button_down_pending = True
                if self.on_button_down:
                    self.on_button_down()
            elif value == 0x00:
                if self._button_down_pending and self.on_click:
                    self.on_click()
                self._button_down_pending = False
                if self.on_button_up:
                    self.on_button_up()
