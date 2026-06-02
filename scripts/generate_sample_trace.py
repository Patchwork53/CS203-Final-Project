#!/usr/bin/env python3
"""Generate a tiny synthetic trace for quick baseline sanity checks."""

from __future__ import annotations

SAMPLE = [
    (0x1000, 0xA000, 5),
    (0x1000, 0xA000, 5),
    (0x1000, 0xA000, 7),
    (0x1000, 0xA000, 7),
    (0x2000, 0xB000, 1),
    (0x2000, 0xB000, 2),
    (0x2000, 0xB000, 2),
]

with open("sample_trace.out", "w", encoding="utf-8") as f:
    for pc, addr, value in SAMPLE:
        f.write(f"0x{pc:x}: R 0x{addr:x}, 0x{value:016x}\n")

print("Wrote sample_trace.out")
