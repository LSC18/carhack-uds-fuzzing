#!/usr/bin/env python3
"""Run the first NRC-guided UDS repair PoC in an isolated virtual ECU."""

from __future__ import annotations

import argparse
from pathlib import Path

from ecu import VirtualEcu
from fuzzer import NrcGuidedRunner, RepairEngine


def parse_hex_request(value: str) -> bytes:
    try:
        request = bytes.fromhex(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("request must be hex bytes, e.g. '10'") from exc
    if not request:
        raise argparse.ArgumentTypeError("request must contain at least one byte")
    return request


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the NRC 0x13 -> repair -> positive response PoC"
    )
    parser.add_argument(
        "--request",
        type=parse_hex_request,
        default=parse_hex_request("10"),
        help="initial UDS request as hex bytes (default: 10)",
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=Path("logs/poc_trace.jsonl"),
        help="JSONL trace path (default: logs/poc_trace.jsonl)",
    )
    args = parser.parse_args()

    runner = NrcGuidedRunner(VirtualEcu(), RepairEngine(), args.log)
    result = runner.run(args.request)
    print(f"[LOG] {args.log}")
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
