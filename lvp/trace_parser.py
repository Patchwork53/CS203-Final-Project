"""Parsers for load value trace lines."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Iterator

# Expected line format:
# 0x400123: R 0x7ffc1234abcd, 0x0000000000000042
TRACE_RE = re.compile(
    r"^\s*(0x[0-9a-fA-F]+):\s+R\s+(0x[0-9a-fA-F]+),\s*(0x[0-9a-fA-F]+)\s*$"
)


@dataclass(frozen=True)
class LoadEvent:
    pc: int
    address: int
    value: int


def parse_trace_line(line: str) -> LoadEvent | None:
    match = TRACE_RE.match(line)
    if not match:
        return None
    pc_s, addr_s, value_s = match.groups()
    return LoadEvent(pc=int(pc_s, 16), address=int(addr_s, 16), value=int(value_s, 16))


def iter_trace(path: str) -> Iterator[LoadEvent]:
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            event = parse_trace_line(line)
            if event is not None:
                yield event


def count_parsable(lines: Iterable[str]) -> int:
    return sum(1 for line in lines if parse_trace_line(line) is not None)
