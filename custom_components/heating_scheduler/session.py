"""Pure session rules for Heating Scheduler.

No Home Assistant imports, side effects, or physical switch actions.
The runtime controller will use these rules in a later development lap.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

MIN_MINUTES = 1
MAX_MINUTES = 240


class SessionDecision(str, Enum):
    START = "start"
    ALREADY_RUNNING = "already_running"
    SWITCH_NOT_OFF = "switch_not_off"
    INVALID_DURATION = "invalid_duration"


@dataclass(frozen=True)
class SessionRequest:
    """Validated timed-heating request, in whole minutes."""

    minutes: int

    @property
    def seconds(self) -> int:
        return self.minutes * 60


def evaluate_start(minutes: object, *, timer_active: bool, switch_off: bool) -> SessionDecision:
    """Reject concurrent sessions or requests with unsafe state.

    A bool is not a valid duration even though bool subclasses int.
    """
    if type(minutes) is not int or not MIN_MINUTES <= minutes <= MAX_MINUTES:
        return SessionDecision.INVALID_DURATION
    if timer_active:
        return SessionDecision.ALREADY_RUNNING
    if not switch_off:
        return SessionDecision.SWITCH_NOT_OFF
    return SessionDecision.START


def make_request(minutes: object, *, timer_active: bool, switch_off: bool) -> SessionRequest:
    """Return a request only when it is safe to start; never actuate devices."""
    decision = evaluate_start(minutes, timer_active=timer_active, switch_off=switch_off)
    if decision is not SessionDecision.START:
        raise ValueError(f"Heating session rejected: {decision.value}")
    return SessionRequest(minutes=minutes)
