#!/usr/bin/env python3
"""Copy the pre-rendered entry image for make.fun bounty news-image-20261126.

The front page (``entry.png`` next to this file) was rendered once by
``draw_news.py`` and is committed to this repository. This script only
copies that file to the directory named by ``MAKEFUN_OUTPUT_DIR``
(default ``/output``), or to ``--out``. It uses nothing but the Python
standard library: no Pillow, no system fonts, no network access, so it
runs in the grading sandbox's bare python:3.13 image.

Usage::

    python3 main.py                 # writes $MAKEFUN_OUTPUT_DIR/entry.png
    python3 main.py --out entry.png # writes entry.png to the given path
"""

from __future__ import annotations

import argparse
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
BYTE_LIMIT = 1_048_576  # the bounty caps the entry at 1 MiB
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024


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
        description="Copy the 26 November 2026 front page to entry.png.")
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

    A truncated copy still has a valid IHDR header, so checking the
    last 12 bytes (length 0, type ``IEND``, CRC) is what proves the
    file was copied all the way through.
    """
    with open(path, "rb") as handle:
        handle.seek(-12, os.SEEK_END)
        tail = handle.read(12)
    return len(tail) == 12 and tail[4:8] == b"IEND"


def check_output(path: str) -> tuple[int, int, int]:
    """Fail loudly if the copied file breaks the bounty's size rules.

    The bounty wants exactly a 1024x1024 PNG under 1 MiB, and the file
    must be a complete PNG (ending in an IEND chunk), not a truncated
    copy. Returns (width, height, byte count) once everything checks out.
    """
    byte_count = os.path.getsize(path)
    if byte_count == 0:
        raise ValueError(f"output is empty: {path}")
    if byte_count > BYTE_LIMIT:
        raise ValueError(f"output too large: {byte_count} bytes "
                         f"(limit {BYTE_LIMIT})")
    width, height = read_png_dimensions(path)
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        raise ValueError(f"output must be exactly "
                         f"{EXPECTED_WIDTH}x{EXPECTED_HEIGHT}, "
                         f"got {width}x{height}")
    if not has_iend_chunk(path):
        raise ValueError(f"output is truncated: {path} has no IEND chunk")
    return width, height, byte_count


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not os.path.isfile(SOURCE):
        print(f"error: source image missing: {SOURCE}", file=sys.stderr)
        return 1
    target = resolve_target(args.out)
    parent = os.path.dirname(target)
    if parent:
        os.makedirs(parent, exist_ok=True)

    try:
        shutil.copyfile(SOURCE, target)
        width, height, byte_count = check_output(target)
    except (OSError, ValueError) as problem:
        print(f"error: {problem}", file=sys.stderr)
        return 1
    print(f"wrote {target} ({width}x{height}, {byte_count} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
