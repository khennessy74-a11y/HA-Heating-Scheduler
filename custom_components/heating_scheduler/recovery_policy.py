"""Pure restart/reload policy for a future timed-heating runtime.

This module does not register any Home Assistant lifecycle listeners and
never calls a switch. Restart is intentionally non-resuming until an actual
runtime adapter has been exercised on a disposable Home Assistant instance.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RecoveryAction(str, Enum):
    LEAVE_OFF = "leave_off"
    BLOCK_UNLOAD = "block_unload"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class RecoveryDecision:
    action: RecoveryAction
    reason: str


def on_startup(*, observed_state: str | None, persisted_session: bool) -> RecoveryDecision:
    """Never infer permission to turn heating on after process restart."""
    if observed_state == "off" and not persisted_session:
        return RecoveryDecision(
            RecoveryAction.LEAVE_OFF, "No active session; do not alter switch"
        )
    return RecoveryDecision(
        RecoveryAction.REVIEW_REQUIRED,
        "Do not auto-resume or toggle a possibly externally controlled heater",
    )


def on_unload(*, active_session: bool, observed_state: str | None) -> RecoveryDecision:
    """A loaded session cannot be abandoned without a verified shutdown."""
    if active_session:
        return RecoveryDecision(
            RecoveryAction.BLOCK_UNLOAD,
            "An active session requires an explicit tested shutdown sequence",
        )
    if observed_state not in ("off",):
        return RecoveryDecision(
            RecoveryAction.REVIEW_REQUIRED,
            "Unknown or on state cannot be treated as safely stopped",
        )
    return RecoveryDecision(
        RecoveryAction.LEAVE_OFF, "No session active; preserve switch state"
    )
