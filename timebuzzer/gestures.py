"""Higher-level gesture events built on top of the raw timeBuzzer protocol.

Rotation already carries a direction (sign of the delta), split here into
separate rotate_cw / rotate_ccw callbacks. Tap and tap-and-hold are both
derived from the touch signal (CC 81) by timing how long contact lasts:
released before `hold_threshold` seconds -> tap, still touching once the
threshold elapses -> tap_hold (fired once, immediately, without waiting for
release).
"""

from __future__ import annotations

import threading
from typing import Callable

from .device import TimeBuzzer

DEFAULT_HOLD_THRESHOLD = 0.5  # seconds


class GestureBuzzer:
    def __init__(
        self,
        device: str | None = None,
        hold_threshold: float = DEFAULT_HOLD_THRESHOLD,
        on_rotate_cw: Callable[[int], None] | None = None,
        on_rotate_ccw: Callable[[int], None] | None = None,
        on_tap: Callable[[], None] | None = None,
        on_tap_hold: Callable[[], None] | None = None,
        on_click: Callable[[], None] | None = None,
    ):
        self.hold_threshold = hold_threshold
        self.on_rotate_cw = on_rotate_cw
        self.on_rotate_ccw = on_rotate_ccw
        self.on_tap = on_tap
        self.on_tap_hold = on_tap_hold
        self.on_click = on_click

        self._hold_timer: threading.Timer | None = None
        self._hold_fired = False

        self._tb = TimeBuzzer(
            device=device,
            on_rotate=self._handle_rotate,
            on_touch=self._handle_touch,
            on_click=self._handle_click,
        )

    @property
    def device(self) -> str:
        return self._tb.device

    def start(self) -> None:
        self._tb.start()

    def stop(self) -> None:
        self._cancel_hold_timer()
        self._tb.stop()

    def run(self) -> None:
        self._tb.run()

    def _handle_rotate(self, delta: int) -> None:
        if delta > 0 and self.on_rotate_cw:
            self.on_rotate_cw(delta)
        elif delta < 0 and self.on_rotate_ccw:
            self.on_rotate_ccw(-delta)

    def _handle_touch(self, active: bool) -> None:
        if active:
            self._hold_fired = False
            self._cancel_hold_timer()
            self._hold_timer = threading.Timer(self.hold_threshold, self._fire_hold)
            self._hold_timer.daemon = True
            self._hold_timer.start()
        else:
            self._cancel_hold_timer()
            if not self._hold_fired and self.on_tap:
                self.on_tap()

    def _fire_hold(self) -> None:
        self._hold_fired = True
        if self.on_tap_hold:
            self.on_tap_hold()

    def _cancel_hold_timer(self) -> None:
        if self._hold_timer:
            self._hold_timer.cancel()
            self._hold_timer = None

    def _handle_click(self) -> None:
        if self.on_click:
            self.on_click()
