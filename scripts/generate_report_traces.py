#!/usr/bin/env python3
"""Generate the synthetic traces used in the report."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TRACE_DIR = REPO_ROOT / "traces"


def write_stride_heavy_trace(path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        for i in range(500):
            f.write(f"0x1000: R 0x{0x8000 + i * 8:x}, 0x{0x100000 + i * 4:016x}\n")
            f.write(f"0x2000: R 0x{0x9000 + i * 16:x}, 0x{0x200000 + i * 8:016x}\n")
            f.write(f"0x3000: R 0xa000, 0x{0x300000 + i * 12:016x}\n")


def write_stride_phase_trace(path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        for i in range(250):
            f.write(f"0x4000: R 0xb000, 0x{0x400000 + i * 2:016x}\n")
            f.write(f"0x5000: R 0xc000, 0x{0x500000 + i * 6:016x}\n")
        for i in range(250, 500):
            f.write(
                f"0x4000: R 0xb000, 0x{0x400000 + 250 * 2 + (i - 250) * 8:016x}\n"
            )
            f.write(
                f"0x5000: R 0xc000, 0x{0x500000 + 250 * 6 + (i - 250) * 3:016x}\n"
            )


def write_adversarial_trace(path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        for i in range(2000):
            f.write(f"0x7000: R 0xd000, 0x{i % 2:016x}\n")


def main() -> None:
    TRACE_DIR.mkdir(parents=True, exist_ok=True)

    stride_path = TRACE_DIR / "stride_heavy_trace.out"
    phase_path = TRACE_DIR / "stride_phase_trace.out"
    adversarial_path = TRACE_DIR / "adversarial_no_ml_trace.out"

    write_stride_heavy_trace(stride_path)
    write_stride_phase_trace(phase_path)
    write_adversarial_trace(adversarial_path)

    print(f"Wrote {stride_path}")
    print(f"Wrote {phase_path}")
    print(f"Wrote {adversarial_path}")


if __name__ == "__main__":
    main()
