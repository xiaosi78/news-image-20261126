#!/usr/bin/env python3
"""Build the entry image for make.fun bounty news-image-20261126.

The front page is painted from scratch by :mod:`draw_news` (Pillow
shapes only, no network, no downloaded assets), so running this script
recreates ``entry.png`` byte for byte. The output goes to the directory
named by ``MAKEFUN_OUTPUT_DIR`` (default ``/output``), or to ``--out``.

Usage::

    python3 main.py                 # writes $MAKEFUN_OUTPUT_DIR/entry.png
    python3 main.py --out entry.png # writes entry.png next to this file
"""

from __future__ import annotations

import argparse
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from draw_news import PAGE_HEIGHT, PAGE_WIDTH, render_page, save_page  # noqa: E402

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
BYTE_LIMIT = 1_048_576  # the bounty caps the entry at 1 MiB


def read_png_dimensions(path: str) -> tuple[int, int]:
    """Pull (width, height) out of a PNG's IHDR chunk, stdlib only."""
    with open(path, "rb") as handle:
        head = handle.read(33)
    if head[:8] != PNG_SIGNATURE or head[12:16] != b"IHDR":
        raise ValueError(f"{path} is not a PNG file")
    width, height = struct.unpack(">II", head[16:24])
    return width, height


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render the 26 November 2026 front page to entry.png.")
    parser.add_argument(
        "--out", default=None,
        help="write the PNG to this exact path instead of the output dir")
    return parser.parse_args(argv)


def resolve_target(out_flag: str | None) -> str:
    if out_flag:
        return os.path.abspath(out_flag)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    return os.path.join(out_dir, "entry.png")


def has_iend_chunk(path: str) -> bool:
    """True when the PNG ends with a proper IEND chunk (complete file).

    A truncated write still has a valid IHDR header, so checking the
    last 12 bytes (length 0, type ``IEND``, CRC) is what proves the
    file was written all the way through.
    """
    with open(path, "rb") as handle:
        handle.seek(-12, os.SEEK_END)
        tail = handle.read(12)
    return len(tail) == 12 and tail[4:8] == b"IEND"


def check_output(path: str) -> tuple[int, int, int]:
    """Fail loudly if the render breaks the bounty's size rules.

    The bounty wants exactly a 1024x1024 PNG under 1 MiB, and the file
    must be a complete PNG (ending in an IEND chunk), not a truncated
    write. Returns (width, height, byte count) once everything checks out.
    """
    byte_count = os.path.getsize(path)
    if byte_count == 0:
        raise ValueError(f"output is empty: {path}")
    if byte_count > BYTE_LIMIT:
        raise ValueError(f"output too large: {byte_count} bytes "
                         f"(limit {BYTE_LIMIT})")
    width, height = read_png_dimensions(path)
    if (width, height) != (PAGE_WIDTH, PAGE_HEIGHT):
        raise ValueError(f"output must be exactly "
                         f"{PAGE_WIDTH}x{PAGE_HEIGHT}, got {width}x{height}")
    if not has_iend_chunk(path):
        raise ValueError(f"output is truncated: {path} has no IEND chunk")
    return width, height, byte_count


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    target = resolve_target(args.out)
    parent = os.path.dirname(target)
    if parent:
        os.makedirs(parent, exist_ok=True)

    save_page(render_page(), target)
    try:
        width, height, byte_count = check_output(target)
    except (OSError, ValueError) as problem:
        print(f"error: {problem}", file=sys.stderr)
        return 1
    print(f"wrote {target} ({width}x{height}, {byte_count} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
