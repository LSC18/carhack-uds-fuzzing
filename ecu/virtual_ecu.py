"""Minimal transport-independent UDS virtual ECU.

This module intentionally models only the behavior needed for the first PoC.
It never communicates with a real vehicle, ECU, CAN interface, or network.
"""

from __future__ import annotations

from enum import IntEnum


class Nrc(IntEnum):
    SERVICE_NOT_SUPPORTED = 0x11
    SUBFUNCTION_NOT_SUPPORTED = 0x12
    INCORRECT_MESSAGE_LENGTH_OR_INVALID_FORMAT = 0x13


class VirtualEcu:
    """Small UDS server model supporting DiagnosticSessionControl (SID 0x10)."""

    DIAGNOSTIC_SESSION_CONTROL = 0x10
    POSITIVE_RESPONSE_OFFSET = 0x40
    NEGATIVE_RESPONSE_SID = 0x7F

    def __init__(self) -> None:
        self.active_session = 0x01
        self.supported_sessions = {0x01, 0x03}

    @classmethod
    def _negative_response(cls, request_sid: int, nrc: Nrc) -> bytes:
        return bytes((cls.NEGATIVE_RESPONSE_SID, request_sid, int(nrc)))

    def handle_request(self, request: bytes) -> bytes:
        """Validate one UDS request and return a UDS-formatted response."""
        if not request:
            raise ValueError("UDS request must contain at least one SID byte")

        sid = request[0]

        if sid != self.DIAGNOSTIC_SESSION_CONTROL:
            return self._negative_response(sid, Nrc.SERVICE_NOT_SUPPORTED)

        if len(request) != 2:
            return self._negative_response(
                sid, Nrc.INCORRECT_MESSAGE_LENGTH_OR_INVALID_FORMAT
            )

        subfunction = request[1] & 0x7F
        if subfunction not in self.supported_sessions:
            return self._negative_response(sid, Nrc.SUBFUNCTION_NOT_SUPPORTED)

        self.active_session = subfunction
        return bytes((sid + self.POSITIVE_RESPONSE_OFFSET, request[1]))
