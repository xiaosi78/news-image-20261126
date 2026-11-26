#!/usr/bin/env python3
"""Paint the world-news front page for Thursday, 26 November 2026.

Everything on the page is drawn from scratch with Pillow primitives:
no photographs, no downloaded assets, no network. The six stories are
fixed data, so rendering the same module twice gives the same PNG.

Run directly to (re)create ``entry.png`` next to this file::

    python3 draw_news.py
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Callable, List, Tuple

from PIL import Image, ImageDraw, ImageFont

# ------------------------------------------------------------------ canvas

PAGE_WIDTH = 1024
PAGE_HEIGHT = 1024

NEWSprint = (248, 244, 233)   # warm paper
INK = (20, 20, 20)           # near-black text and rules
PAPER_WHITE = (255, 255, 255)
BODY_GREY = (58, 58, 58)
MUTED = (96, 96, 96)
FLAME = (232, 122, 22)

# One accent colour per story, used for its spine, icon frame and icon.
CRIMSON = (176, 32, 32)
OCEAN = (26, 58, 112)
PLUM = (96, 62, 138)
PINE = (36, 108, 56)
TEAL = (0, 108, 108)
EMBER = (198, 88, 0)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_BOLD = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
SANS_PLAIN = os.path.join(FONT_DIR, "DejaVuSans.ttf")


@dataclass
class Typefaces:
    """The four sizes this page needs, loaded once."""

    masthead: ImageFont.FreeTypeFont
    dateline: ImageFont.FreeTypeFont
    kicker: ImageFont.FreeTypeFont
    headline: ImageFont.FreeTypeFont
    summary: ImageFont.FreeTypeFont
    footnote: ImageFont.FreeTypeFont

    @classmethod
    def load(cls) -> "Typefaces":
        def at(path: str, size: int) -> ImageFont.FreeTypeFont:
            return ImageFont.truetype(path, size)

        return cls(
            masthead=at(SERIF_BOLD, 88),
            dateline=at(SANS_BOLD, 32),
            kicker=at(SANS_PLAIN, 20),
            headline=at(SANS_BOLD, 26),
            summary=at(SANS_PLAIN, 20),
            footnote=at(SANS_PLAIN, 15),
        )


# ------------------------------------------------------------------ stories

IconPainter = Callable[[ImageDraw.ImageDraw, float, float, float, Tuple[int, int, int]], None]


@dataclass
class Story:
    headline: str
    deck: str
    accent: Tuple[int, int, int]
    paint: IconPainter


def _rocket(pen, cx, cy, radius, colour):
    """A capsule climbing, drawn around its centre point."""
    w = radius * 0.62          # half-width of the body
    nose = cy - radius
    tail = cy + radius * 0.55
    # body: pointed nose, straight sides, flat tail
    pen.polygon(
        [(cx, nose), (cx + w, nose + radius * 0.55), (cx + w, tail),
         (cx - w, tail), (cx - w, nose + radius * 0.55)],
        fill=colour,
    )
    # fins
    pen.polygon([(cx - w, tail - radius * 0.35), (cx - w - radius * 0.45, tail + radius * 0.28),
                 (cx - w, tail)], fill=colour)
    pen.polygon([(cx + w, tail - radius * 0.35), (cx + w + radius * 0.45, tail + radius * 0.28),
                 (cx + w, tail)], fill=colour)
    # porthole
    r = radius * 0.26
    pen.ellipse([cx - r, cy - radius * 0.28 - r, cx + r, cy - radius * 0.28 + r],
                fill=PAPER_WHITE, outline=colour, width=2)
    # exhaust flame below the tail
    pen.polygon([(cx - w * 0.55, tail), (cx + w * 0.55, tail),
                 (cx, tail + radius * 0.5)], fill=FLAME)
    # two sparks
    for sx, sy in ((cx - radius * 0.95, cy - radius * 0.55),
                   (cx + radius * 0.95, cy - radius * 0.75)):
        _spark(pen, sx, sy, radius * 0.14, colour)


def _spark(pen, cx, cy, size, colour):
    """A tiny four-point star used as a space sparkle."""
    pen.polygon([(cx, cy - size), (cx + size * 0.28, cy - size * 0.28),
                 (cx + size, cy), (cx + size * 0.28, cy + size * 0.28),
                 (cx, cy + size), (cx - size * 0.28, cy + size * 0.28),
                 (cx - size, cy), (cx - size * 0.28, cy - size * 0.28)],
                fill=colour)


def _tariff_bars(pen, cx, cy, radius, colour):
    """Four rising columns under a climbing arrow: duties going up."""
    base = cy + radius * 0.85
    pen.line([cx - radius, base, cx + radius, base], fill=colour, width=4)
    pen.line([cx - radius, base, cx - radius, cy - radius * 0.85], fill=colour, width=4)
    heights = (0.30, 0.52, 0.70, 0.92)
    slot = radius * 2 / len(heights)
    for step, frac in enumerate(heights):
        left = cx - radius + step * slot + slot * 0.14
        right = left + slot * 0.72
        top = base - radius * 1.7 * frac
        pen.rectangle([left, top, right, base], fill=colour)
    # red arrow riding over the column tops
    pen.line([cx - radius * 0.8, cy + radius * 0.15,
              cx + radius * 0.85, cy - radius * 0.85], fill=CRIMSON, width=5)
    pen.polygon([(cx + radius * 0.85, cy - radius * 0.85),
                 (cx + radius * 0.45, cy - radius * 0.82),
                 (cx + radius * 0.82, cy - radius * 0.45)], fill=CRIMSON)


def _closed_door(pen, cx, cy, radius, colour):
    """A doorway crossed out: an envoy ordered to leave."""
    left, right = cx - radius * 0.6, cx + radius * 0.6
    top, bottom = cy - radius * 0.9, cy + radius * 0.9
    pen.rectangle([left, top, right, bottom], outline=colour, width=5)
    pen.line([cx, top, cx, bottom], fill=colour, width=3)
    pen.line([left - radius * 0.12, top - radius * 0.12,
              right + radius * 0.12, bottom + radius * 0.12], fill=CRIMSON, width=6)
    pen.line([right + radius * 0.12, top - radius * 0.12,
              left - radius * 0.12, bottom + radius * 0.12], fill=CRIMSON, width=6)


def _wage_shirt(pen, cx, cy, radius, colour):
    """A worker's shirt with a pay-rise arrow beside it."""
    r = radius
    pen.polygon(
        [(cx - r * 0.34, cy - r * 0.82), (cx - r * 0.14, cy - r * 0.62),
         (cx + r * 0.14, cy - r * 0.62), (cx + r * 0.34, cy - r * 0.82),
         (cx + r * 0.78, cy - r * 0.5), (cx + r * 0.6, cy - r * 0.28),
         (cx + r * 0.52, cy - r * 0.34), (cx + r * 0.52, cy + r * 0.85),
         (cx - r * 0.52, cy + r * 0.85), (cx - r * 0.52, cy - r * 0.34),
         (cx - r * 0.6, cy - r * 0.28), (cx - r * 0.78, cy - r * 0.5)],
        fill=colour,
    )
    # collar seam
    pen.line([cx - r * 0.14, cy - r * 0.62, cx, cy - r * 0.44,
              cx + r * 0.14, cy - r * 0.62], fill=PAPER_WHITE, width=2)
    # rising arrow to the right of the shirt
    ax = cx + r * 0.92
    pen.line([ax, cy + r * 0.8, ax, cy - r * 0.7], fill=FLAME, width=5)
    pen.polygon([(ax, cy - r * 0.92), (ax - r * 0.18, cy - r * 0.6),
                 (ax + r * 0.18, cy - r * 0.6)], fill=FLAME)


def _pact_shield(pen, cx, cy, radius, colour):
    """A shield with a tick inside: a security partnership."""
    r = radius
    pen.polygon([(cx, cy - r), (cx + r * 0.82, cy - r * 0.68),
                 (cx + r * 0.82, cy + r * 0.1), (cx, cy + r),
                 (cx - r * 0.82, cy + r * 0.1), (cx - r * 0.82, cy - r * 0.68)],
                fill=colour)
    pen.polygon([(cx, cy - r * 0.78), (cx + r * 0.6, cy - r * 0.52),
                 (cx + r * 0.6, cy + r * 0.08), (cx, cy + r * 0.74),
                 (cx - r * 0.6, cy + r * 0.08), (cx - r * 0.6, cy - r * 0.52)],
                fill=PAPER_WHITE)
    pen.line([cx - r * 0.34, cy + r * 0.02, cx - r * 0.08, cy + r * 0.28,
              cx + r * 0.4, cy - r * 0.28], fill=colour, width=6)


def _freed_shop(pen, cx, cy, radius, colour):
    """A corner shop with a striped awning: hostages walked out free."""
    r = radius
    # shop body and door
    pen.rectangle([cx - r * 0.8, cy - r * 0.2, cx + r * 0.8, cy + r * 0.9],
                  outline=colour, width=4)
    pen.rectangle([cx - r * 0.16, cy + r * 0.28, cx + r * 0.16, cy + r * 0.9],
                  fill=colour)
    # windows
    pen.rectangle([cx - r * 0.66, cy + r * 0.08, cx - r * 0.3, cy + r * 0.42],
                  outline=colour, width=3)
    pen.rectangle([cx + r * 0.3, cy + r * 0.08, cx + r * 0.66, cy + r * 0.42],
                  outline=colour, width=3)
    # awning slab with light stripes
    pen.polygon([(cx - r * 0.92, cy - r * 0.2), (cx + r * 0.92, cy - r * 0.2),
                 (cx + r * 0.78, cy - r * 0.62), (cx - r * 0.78, cy - r * 0.62)],
                fill=colour)
    for step in range(4):
        ax = cx - r * 0.6 + step * r * 0.4
        pen.line([ax, cy - r * 0.2, ax + r * 0.08, cy - r * 0.62],
                 fill=PAPER_WHITE, width=3)
    # small green tick above the roof: everyone got out
    pen.line([cx - r * 0.14, cy - r * 0.78, cx, cy - r * 0.64,
              cx + r * 0.2, cy - r * 0.94], fill=PINE, width=4)


def all_stories() -> List[Story]:
    """The six verified stories of 26 November 2026, in page order."""
    return [
        Story(
            headline="SHENZHOU-24 REACHES TIANGONG",
            deck="Pakistan's Muhammad Zeeshan Ali becomes the first foreign "
                 "astronaut aboard China's space station.",
            accent=OCEAN, paint=_rocket,
        ),
        Story(
            headline="US TARIFFS HIT 14 PARTNERS",
            deck="Washington proposes duties up to 25% on India and 35% on "
                 "Vietnam; trade deals could cut them.",
            accent=CRIMSON, paint=_tariff_bars,
        ),
        Story(
            headline="N. KOREA EXPELS SWISS ENVOY",
            deck="Pyongyang shuts the Swiss office weeks after it reopened "
                 "and orders its head out within 48 hours.",
            accent=PLUM, paint=_closed_door,
        ),
        Story(
            headline="BANGLADESH WAGE UP 36%",
            deck="Garment workers win a rise to 17,000 taka after weeks of "
                 "protests that shut factories.",
            accent=TEAL, paint=_wage_shirt,
        ),
        Story(
            headline="SOLOMONS PICK AUSTRALIA",
            deck="Treaty makes Canberra the primary security partner; no "
                 "foreign military bases on its soil.",
            accent=PINE, paint=_pact_shield,
        ),
        Story(
            headline="CARTAGENA HOSTAGES FREED",
            deck="All 20 rescued after a 17-hour supermarket siege; one "
                 "captor killed in the storming.",
            accent=EMBER, paint=_freed_shop,
        ),
    ]


FOOTNOTE = ("Sources: Xinhua  ·  USTR  ·  KCNA  ·  Dhaka wage board  ·  "
            "Canberra  ·  Bogota")


# ------------------------------------------------------------------ helpers

def fit_lines(pen: ImageDraw.ImageDraw, text: str,
              typeface: ImageFont.FreeTypeFont, width: int) -> List[str]:
    """Split *text* into lines no wider than *width* pixels."""
    lines: List[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if pen.textlength(candidate, font=typeface) <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def paragraph(pen: ImageDraw.ImageDraw, x: int, y: int, lines: List[str],
              typeface: ImageFont.FreeTypeFont, colour: Tuple[int, int, int],
              leading: int) -> int:
    """Draw *lines* top to bottom; return the y just below the last one."""
    for line in lines:
        pen.text((x, y), line, font=typeface, fill=colour)
        y += leading
    return y


# ------------------------------------------------------------------ the page

@dataclass
class FrontPage:
    """A 1024x1024 newspaper front page, painted panel by panel."""

    faces: Typefaces = field(default_factory=Typefaces.load)
    stories: List[Story] = field(default_factory=all_stories)

    # grid geometry, worked out once here so panels never overlap
    edge: int = 30        # outer margin on the left and right
    gap: int = 18         # space between neighbouring panels
    grid_top: int = 238   # first row starts below the masthead block
    grid_bottom: int = 966

    @property
    def column_width(self) -> int:
        return (PAGE_WIDTH - 2 * self.edge - self.gap) // 2

    @property
    def row_height(self) -> int:
        return (self.grid_bottom - self.grid_top - 2 * self.gap) // 3

    def build(self) -> Image.Image:
        sheet = Image.new("RGB", (PAGE_WIDTH, PAGE_HEIGHT), NEWSprint)
        pen = ImageDraw.Draw(sheet)
        pen.rectangle([0, 0, PAGE_WIDTH - 1, PAGE_HEIGHT - 1],
                      outline=INK, width=5)
        self._masthead(pen)
        for index, story in enumerate(self.stories):
            column, row = index % 2, index // 2
            self._panel(pen, story, column, row)
        self._footnote(pen)
        return sheet

    def _masthead(self, pen: ImageDraw.ImageDraw) -> None:
        centre = PAGE_WIDTH // 2
        pen.text((centre, 24), "WORLD NEWS", font=self.faces.masthead,
                 fill=INK, anchor="ma")
        pen.text((centre, 128), "Thursday, 26 November 2026",
                 font=self.faces.dateline, fill=INK, anchor="ma")
        pen.line([36, 176, PAGE_WIDTH - 36, 176], fill=INK, width=3)
        pen.line([36, 182, PAGE_WIDTH - 36, 182], fill=INK, width=1)
        pen.text((centre, 190), "THE DAY IN SIX STORIES",
                 font=self.faces.kicker, fill=MUTED, anchor="ma")

    def _panel(self, pen: ImageDraw.ImageDraw, story: Story,
               column: int, row: int) -> None:
        x0 = self.edge + column * (self.column_width + self.gap)
        y0 = self.grid_top + row * (self.row_height + self.gap)
        x1 = x0 + self.column_width
        y1 = y0 + self.row_height
        pen.rectangle([x0, y0, x1, y1], fill=PAPER_WHITE, outline=INK, width=2)
        pen.rectangle([x0, y0, x0 + 7, y1], fill=story.accent)

        # square icon cell on the left of the panel
        cell = 112
        ix, iy = x0 + 16, y0 + 18
        pen.rectangle([ix, iy, ix + cell, iy + cell],
                      outline=story.accent, width=2)
        story.paint(pen, ix + cell / 2, iy + cell / 2, cell / 2 - 6,
                    story.accent)

        # headline + one-line summary on the right of the icon
        tx = ix + cell + 16
        tw = x1 - 12 - tx
        top = y0 + 20
        head = fit_lines(pen, story.headline, self.faces.headline, tw)
        after_head = paragraph(pen, tx, top, head, self.faces.headline,
                               INK, 31)
        body = fit_lines(pen, story.deck, self.faces.summary, tw)
        paragraph(pen, tx, after_head + 10, body, self.faces.summary,
                  BODY_GREY, 25)

    def _footnote(self, pen: ImageDraw.ImageDraw) -> None:
        pen.text((PAGE_WIDTH // 2, PAGE_HEIGHT - 40), FOOTNOTE,
                 font=self.faces.footnote, fill=MUTED, anchor="ma")


def render_page() -> Image.Image:
    """Build the front page image; pure function of the data above."""
    return FrontPage().build()


def save_page(image: Image.Image, path: str) -> int:
    """Save *image* as an optimised PNG; return the byte count."""
    image.save(path, "PNG", optimize=True)
    return os.path.getsize(path)


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    target = os.path.join(here, "entry.png")
    size = save_page(render_page(), target)
    print(f"wrote {target} ({PAGE_WIDTH}x{PAGE_HEIGHT}, {size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
